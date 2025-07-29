from django.conf import settings
from django.contrib.postgres.search import SearchQuery
from django.db import transaction
from django.db.models import F, Q, Window
from django.db.models.functions import DenseRank
from django.dispatch import receiver
from pgvector.django import CosineDistance

from torque import models as torque_models
from torque.signals import search_filter, search_index_rebuilt, update_cache_document

from semantic_search.llm import llm, local_llm
from semantic_search.models import SemanticSearchCacheDocument
from semantic_search.utils import build_semantic_summary, filter_queries

from semantic_search.embedding_cache import embeddings_cache

BATCH_SIZE = 32 * 4


@receiver(update_cache_document)
def update_semantic_cache_document(sender, **kwargs):
    cache_document = kwargs["cache_document"]
    filtered_data = kwargs["filtered_data"]
    document_dict = kwargs["document_dict"]

    with transaction.atomic():
        SemanticSearchCacheDocument.objects.filter(
            search_cache_document=cache_document
        ).delete()

        semantic_summary = build_semantic_summary(document_dict, filtered_data)

        embeddings = embeddings_cache.get(semantic_summary)

        if not embeddings:
            embeddings = local_llm.get_embeddings(semantic_summary)
            embeddings_cache.add(semantic_summary, embeddings)

        semantic_search_cache_documents = [
            SemanticSearchCacheDocument(
                search_cache_document=cache_document,
                data=semantic_summary,
                data_embedding=embedding,
            )
            for embedding in embeddings
        ]

        SemanticSearchCacheDocument.objects.bulk_create(semantic_search_cache_documents)


@receiver(search_index_rebuilt)
def rebuild_semantic_search_index(sender, **kwargs):
    wiki_config = kwargs["wiki_config"]

    search_cache_documents = torque_models.SearchCacheDocument.objects.filter(
        wiki_config=wiki_config
    )
    scds_to_fetch = []
    semantic_summaries_to_fetch = []
    llm_embeddings = []
    semantic_sc_documents = []
    for scd in search_cache_documents:
        document_dict = scd.document.to_dict(wiki_config, "latest")["fields"]
        semantic_summary = build_semantic_summary(document_dict, scd.filtered_data)

        embeddings = embeddings_cache.get(semantic_summary)

        if embeddings:
            semantic_sc_documents.append(
                SemanticSearchCacheDocument(
                    search_cache_document=scd,
                    data_embedding=embeddings,
                    data=semantic_summary,
                )
            )
        else:
            scds_to_fetch.append(scd)
            semantic_summaries_to_fetch.append(semantic_summary)

            if len(semantic_summaries_to_fetch) % BATCH_SIZE == 0:
                llm_embeddings.extend(llm.get_embeddings(semantic_summaries_to_fetch[-BATCH_SIZE:]))

    if semantic_summaries_to_fetch:
        llm_embeddings.extend(
            llm.get_embeddings(
                semantic_summaries_to_fetch[-(len(semantic_summaries_to_fetch) % BATCH_SIZE) :]
            )
        )

    for scd, (semantic_summary, embedding) in zip(scds_to_fetch,
            zip(semantic_summaries_to_fetch, llm_embeddings)
        ):
        embeddings_cache.add(semantic_summary, embedding)
        semantic_sc_documents.append(
            SemanticSearchCacheDocument(
                search_cache_document=scd,
                data_embedding=embedding,
                data=semantic_summary,
            )
        )

    SemanticSearchCacheDocument.objects.bulk_create(semantic_sc_documents)


@receiver(search_filter)
def semantic_filter(sender, **kwargs):
    similarity = getattr(settings, "SEMANTIC_SEARCH_SIMILARITY", 0.7)

    cache_documents = kwargs["cache_documents"]
    qs = kwargs.get("qs")
    qs_without_negations = filter_queries(qs, keep_negations=False)

    if qs_without_negations:
        embeddings = local_llm.get_embeddings(qs_without_negations, prompt_name="query")

        distances = {}
        semantic_qs = Q()
        for i, embedding in enumerate(embeddings):
            distance_col_name = f"distance_{i}"
            distances[distance_col_name] = CosineDistance(
                "semantic_documents__data_embedding", embedding
            )
            semantic_qs |= Q(**{f"{distance_col_name}__lte": similarity})

        # filters phrases and negations from the queries,
        # what we're calling exact or advanced search
        filter_qs = Q()
        for q in filter_queries(qs):
            if q != "":
                filter_qs &= Q(data_vector=SearchQuery(q, search_type="websearch"))

        results = (
            cache_documents
                .alias(**distances)
                .annotate(
                    score=1 - F("distance_0")
                )
                .filter(semantic_qs)
                .filter(filter_qs)
        )

        return results
