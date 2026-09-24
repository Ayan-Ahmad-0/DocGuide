from src.citations import extract_citations, find_unsupported


def test_extract_basic():
    txt = "Data must be lawful [Article 5(1)]. Retention is limited [Article 5(1)] [Recital 39]."
    assert extract_citations(txt) == ["Article 5(1)", "Article 5(1)", "Recital 39"]


def test_extract_combined_brackets():
    txt = "x [Article 5(1); Recital 39] y [Article 6, Article 7(1)]"
    assert extract_citations(txt) == ["Article 5(1)", "Recital 39", "Article 6", "Article 7(1)"]


def test_supported_within_range():
    assert find_unsupported(["Article 7(1)"], ["Article 7(1)-(2)"]) == []
    assert find_unsupported(["Article 83(5)"], ["Article 83(4)"]) == ["Article 83(5)"]


def test_article_level_and_subpoint():
    assert find_unsupported(["Article 83"], ["Article 83(5)"]) == []
    assert find_unsupported(["Article 5(1)(a)"], ["Article 5(1)"]) == []


def test_invented_citation():
    assert find_unsupported(["Recital 999"], ["Recital 39"]) == ["Recital 999"]