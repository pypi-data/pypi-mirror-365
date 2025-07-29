from django.conf import settings
from luqum.parser import parser

from semantic_search.transformers import (
    FilterQueryTransformer,
    WithoutNegationsTransformer,
)


def filter_queries(qs, keep_negations=True):
    """
    Filters a list of queries to keep only phrases, e.g. "term", and
    negations, and some operators,
    e.g. `title:water water in india -"is a resource" -goats "test"`
    becomes `-"is a resource" -goats "test"`.
    Or just removes negations.
    """

    Transformer = (
        FilterQueryTransformer
        if keep_negations
        else WithoutNegationsTransformer
    )

    return [str(Transformer().visit(parser.parse(q))).strip() for q in qs]


def build_semantic_summary(document_dict, filtered_data):
    embedding_data = {}

    for filter in getattr(settings, "SEMANTIC_SEARCH_ADDITIONAL_FILTERS", []):
        embedding_data[filter.name()] = filter.document_value(document_dict)

    embedding_data.update(filtered_data)

    data_text = ""
    for name, value in embedding_data.items():
        name = name.replace("_", " ")
        if isinstance(value, list):
            for v in value:
                data_text += f"{name} is {v}. "
        elif value:
            data_text += f"{name} is {value}. "

    return data_text
