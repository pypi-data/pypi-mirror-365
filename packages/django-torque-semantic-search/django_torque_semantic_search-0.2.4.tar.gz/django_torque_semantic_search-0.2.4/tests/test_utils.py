import pytest
from semantic_search.utils import filter_queries


@pytest.mark.parametrize(
    "query,expected_result",
    [
        # should remove all words
        ("water in india", ""),
        # should keep negated words
        ("-test", "-test"),
        # should remove all words except negated
        ("water in india -test", "-test"),
        # should remove words, keep negated phrase
        (
            'water in india -"test 123"',
            '-"test 123"',
        ),
        # should not remove words when OR-ed
        ('water OR "test"', 'water OR "test"'),
        # should keeps a phrase
        ('water AND "test"', '"test"'),
        # should remove AND, group where none of the terms are retained
        (
            "(water AND test)",
            "",
        ),
        # should keep negated term in AND, retain group
        ("(water AND -test)", "( -test)"),
        # should remove NOT (search doesn't yet support NOT), non-negated word
        ("NOT water", ""),
        # should keep phrase, remove NOT
        (
            'NOT "test"',
            '"test"',
        ),
        # all together now
        (
            'title:water water in india -"is a resource" -goats "test"',
            '-"is a resource" -goats "test"',
        ),
    ],
)
def test_filter_queries(query, expected_result):
    results = filter_queries([query])
    assert results[0] == expected_result, (
        f"Expected {expected_result}, but got {results}"
    )


@pytest.mark.parametrize(
    "query,expected_result",
    [
        ("-test", ""),
        (
            'title:water water in india -"is a resource" -goats "test"',
            'title:water water in india "test"',
        ),
    ],
)
def test_filter_queries_without_negations(query, expected_result):
    results = filter_queries([query], keep_negations=False)
    assert results[0] == expected_result, (
        f"Expected {expected_result}, but got {results}"
    )
