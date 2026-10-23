"""Unit tests for search client, extractor, text similarity, and page fetcher."""

from content_agent.tools.search_client import SearchClient
from content_agent.tools.extractor import Extractor
from content_agent.tools.embeddings import TextSimilarity


def test_search_client_curated_fallback():
    client = SearchClient(force_offline=True)
    sources, is_live, explanation = client.search(query="Autonomous Agents", max_results=3)
    assert len(sources) == 3
    assert is_live is False
    assert sources[0].id == 1
    assert "Autonomous Agents" in sources[0].title


def test_extractor_utilities():
    md = """# Main Header
Paragraph with citation [1] and [2].
## Section A
See [Reference Site](https://example.com/ref).
"""
    headings = Extractor.extract_headings(md)
    assert len(headings) == 2
    assert headings[0]["title"] == "Main Header"
    assert headings[0]["level"] == 1

    citations = Extractor.extract_citations(md)
    assert citations == [1, 2]

    links = Extractor.extract_links(md)
    assert len(links) == 1
    assert links[0]["anchor"] == "Reference Site"
    assert links[0]["url"] == "https://example.com/ref"


def test_text_similarity():
    t1 = "Machine learning models require robust validation datasets."
    t2 = "Machine learning models need robust training datasets."
    sim = TextSimilarity.cosine_similarity(t1, t2)
    assert sim > 0.6

    t3 = "The pizza crust was crispy and delicious."
    sim_unrelated = TextSimilarity.cosine_similarity(t1, t3)
    assert sim_unrelated < 0.2
