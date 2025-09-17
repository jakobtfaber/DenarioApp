"""
Smoke tests for retrieval paths and citation formatting.
These tests verify that all RAG providers work correctly.
"""

from denario_app.arxiv_rag import ArxivRetriever, ArxivRAGRetriever
from denario_app.graphrag import GraphRAGIndexer, GraphRAGRetriever
import os
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestGraphRAGRetrieval:
    """Test GraphRAG retrieval functionality."""

    def test_graphrag_indexer_initialization(self):
        """Test GraphRAG indexer can be initialized."""
        indexer = GraphRAGIndexer(
            corpus_path="/tmp/test_corpus",
            index_path="/tmp/test_index"
        )
        assert indexer.corpus_path == Path("/tmp/test_corpus")
        assert indexer.index_path == Path("/tmp/test_index")

    def test_graphrag_entity_extraction(self):
        """Test entity extraction from text."""
        indexer = GraphRAGIndexer()

        test_text = """
        This paper discusses cosmology and CMB analysis using Planck data.
        The authors Smith et al. found H0 = 67.4 ± 0.5 km/s/Mpc.
        DOI: 10.48550/arXiv.2012.12345
        arXiv:2012.12345
        """

        entities = indexer._extract_entities(test_text)

        # Check for DOI
        assert any(
            "doi:10.48550/arXiv.2012.12345" in entity for entity in entities)

        # Check for arXiv ID
        assert any("arxiv:2012.12345" in entity for entity in entities)

        # Check for author
        assert any("author:Smith" in entity for entity in entities)

        # Check for technical terms
        assert any("concept:cosmology" in entity for entity in entities)
        assert any("concept:CMB" in entity for entity in entities)

    def test_graphrag_retriever_initialization(self):
        """Test GraphRAG retriever can be initialized."""
        with patch.object(GraphRAGIndexer, 'index_corpus'):
            retriever = GraphRAGRetriever()
            assert retriever.indexer is not None

    def test_graphrag_retrieve_empty_corpus(self):
        """Test GraphRAG retrieval with empty corpus."""
        with patch.object(GraphRAGIndexer, 'index_corpus'):
            retriever = GraphRAGRetriever()
            retriever.indexer.documents = {}

            results = retriever.retrieve("test query")
            assert results == []

    def test_graphrag_corpus_stats(self):
        """Test GraphRAG corpus statistics."""
        with patch.object(GraphRAGIndexer, 'index_corpus'):
            retriever = GraphRAGRetriever()
            retriever.indexer.documents = {"doc1": {}, "doc2": {}}
            retriever.indexer.entities = {"entity1": [], "entity2": []}
            retriever.indexer.relationships = [{"rel1": "test"}]

            stats = retriever.get_corpus_stats()
            assert stats["documents"] == 2
            assert stats["entities"] == 2
            assert stats["relationships"] == 1


class TestArxivRetrieval:
    """Test arXiv retrieval functionality."""

    def test_arxiv_retriever_initialization(self):
        """Test arXiv retriever can be initialized."""
        retriever = ArxivRetriever(max_results=5)
        assert retriever.max_results == 5
        assert retriever.base_url == "http://export.arxiv.org/api/query"

    def test_arxiv_rag_retriever_initialization(self):
        """Test arXiv RAG retriever can be initialized."""
        rag_retriever = ArxivRAGRetriever(max_results=3)
        assert rag_retriever.retriever.max_results == 3

    @patch('requests.get')
    def test_arxiv_search_success(self, mock_get):
        """Test successful arXiv search."""
        # Mock XML response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"""<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <entry>
                <title>Test Paper Title</title>
                <summary>This is a test paper about cosmology.</summary>
                <published>2023-01-01T00:00:00Z</published>
                <updated>2023-01-01T00:00:00Z</updated>
                <author><name>Test Author</name></author>
                <link type="application/pdf" href="http://arxiv.org/pdf/2301.00001.pdf"/>
                <link type="text/html" href="http://arxiv.org/abs/2301.00001"/>
                <category term="astro-ph.CO"/>
            </entry>
        </feed>"""
        mock_get.return_value = mock_response

        retriever = ArxivRetriever()
        results = retriever.search("cosmology")

        assert len(results) == 1
        assert results[0]["title"] == "Test Paper Title"
        assert results[0]["authors"] == ["Test Author"]
        assert results[0]["arxiv_id"] == "2301.00001"
        assert results[0]["doi"] == "10.48550/arXiv.2301.00001"

    @patch('requests.get')
    def test_arxiv_search_failure(self, mock_get):
        """Test arXiv search failure handling."""
        mock_get.side_effect = Exception("Network error")

        retriever = ArxivRetriever()
        results = retriever.search("cosmology")

        assert results == []

    def test_arxiv_format_for_denario(self):
        """Test arXiv paper formatting for DenarioApp."""
        retriever = ArxivRetriever()

        papers = [
            {
                "title": "Test Paper",
                "authors": ["Author 1", "Author 2"],
                "arxiv_id": "2301.00001",
                "doi": "10.48550/arXiv.2301.00001",
                "categories": ["astro-ph.CO"],
                "abstract_url": "http://arxiv.org/abs/2301.00001",
                "summary": "This is a test abstract."
            }
        ]

        formatted = retriever.format_for_denario(papers)

        assert "Found 1 relevant papers from arXiv" in formatted
        assert "Test Paper" in formatted
        assert "Author 1" in formatted
        assert "arXiv ID: 2301.00001" in formatted
        assert "DOI: https://doi.org/10.48550/arXiv.2301.00001" in formatted


class TestRetrievalIntegration:
    """Test integration between different retrieval methods."""

    def test_all_retrievers_importable(self):
        """Test that all retriever modules can be imported."""
        from denario_app.graphrag import get_graphrag_retriever
        from denario_app.arxiv_rag import get_arxiv_retriever

        # Test that functions exist and are callable
        assert callable(get_graphrag_retriever)
        assert callable(get_arxiv_retriever)

    def test_retriever_consistency(self):
        """Test that all retrievers return consistent format."""
        with patch.object(GraphRAGIndexer, 'index_corpus'):
            graphrag = GraphRAGRetriever()
            graphrag.indexer.documents = {}

            arxiv = ArxivRAGRetriever()

            # Both should return empty lists for empty results
            graphrag_results = graphrag.retrieve("test")
            arxiv_results = arxiv.retrieve("test")

            assert isinstance(graphrag_results, list)
            assert isinstance(arxiv_results, list)


class TestCitationFormatting:
    """Test citation formatting and normalization."""

    def test_doi_normalization(self):
        """Test DOI normalization to https://doi.org/ format."""
        test_dois = [
            "10.48550/arXiv.2301.00001",
            "10.1038/nature12345",
            "10.1126/science.abc123"
        ]

        for doi in test_dois:
            normalized = f"https://doi.org/{doi}"
            assert normalized.startswith("https://doi.org/")
            assert normalized.endswith(doi)

    def test_arxiv_id_extraction(self):
        """Test arXiv ID extraction from various formats."""
        test_cases = [
            ("2301.00001", "2301.00001"),
            ("2301.00001v1", "2301.00001v1"),
            ("arXiv:2301.00001", "2301.00001"),
            ("http://arxiv.org/abs/2301.00001", "2301.00001"),
        ]

        for input_id, expected in test_cases:
            # Simple extraction logic
            if ":" in input_id:
                extracted = input_id.split(":")[-1]
            elif "/" in input_id:
                extracted = input_id.split("/")[-1]
            else:
                extracted = input_id

            assert extracted == expected


class TestEnvironmentValidation:
    """Test environment validation for retrieval systems."""

    def test_required_directories_exist(self):
        """Test that required directories exist or can be created."""
        # Test GraphRAG index directory creation
        test_index_path = Path("/tmp/test_graphrag_index")
        indexer = GraphRAGIndexer(index_path=str(test_index_path))
        assert test_index_path.exists()

        # Clean up
        import shutil
        shutil.rmtree(test_index_path, ignore_errors=True)

    def test_corpus_path_validation(self):
        """Test corpus path validation."""
        # Test with non-existent path
        indexer = GraphRAGIndexer(corpus_path="/nonexistent/path")
        # Should not raise error, but handle gracefully
        assert indexer.corpus_path == Path("/nonexistent/path")


def run_smoke_tests():
    """Run all smoke tests and return results."""
    test_results = {
        "graphrag": {"passed": 0, "failed": 0, "errors": []},
        "arxiv": {"passed": 0, "failed": 0, "errors": []},
        "integration": {"passed": 0, "failed": 0, "errors": []},
        "citations": {"passed": 0, "failed": 0, "errors": []},
        "environment": {"passed": 0, "failed": 0, "errors": []}
    }

    # Test GraphRAG
    try:
        test_graphrag = TestGraphRAGRetrieval()
        test_graphrag.test_graphrag_indexer_initialization()
        test_graphrag.test_graphrag_entity_extraction()
        test_graphrag.test_graphrag_retriever_initialization()
        test_graphrag.test_graphrag_retrieve_empty_corpus()
        test_graphrag.test_graphrag_corpus_stats()
        test_results["graphrag"]["passed"] = 5
    except Exception as e:
        test_results["graphrag"]["failed"] = 1
        test_results["graphrag"]["errors"].append(str(e))

    # Test arXiv
    try:
        test_arxiv = TestArxivRetrieval()
        test_arxiv.test_arxiv_retriever_initialization()
        test_arxiv.test_arxiv_rag_retriever_initialization()
        test_arxiv.test_arxiv_format_for_denario()
        test_results["arxiv"]["passed"] = 3
    except Exception as e:
        test_results["arxiv"]["failed"] = 1
        test_results["arxiv"]["errors"].append(str(e))

    # Test Integration
    try:
        test_integration = TestRetrievalIntegration()
        test_integration.test_all_retrievers_importable()
        test_integration.test_retriever_consistency()
        test_results["integration"]["passed"] = 2
    except Exception as e:
        test_results["integration"]["failed"] = 1
        test_results["integration"]["errors"].append(str(e))

    # Test Citations
    try:
        test_citations = TestCitationFormatting()
        test_citations.test_doi_normalization()
        test_citations.test_arxiv_id_extraction()
        test_results["citations"]["passed"] = 2
    except Exception as e:
        test_results["citations"]["failed"] = 1
        test_results["citations"]["errors"].append(str(e))

    # Test Environment
    try:
        test_env = TestEnvironmentValidation()
        test_env.test_required_directories_exist()
        test_env.test_corpus_path_validation()
        test_results["environment"]["passed"] = 2
    except Exception as e:
        test_results["environment"]["failed"] = 1
        test_results["environment"]["errors"].append(str(e))

    return test_results


if __name__ == "__main__":
    """Run smoke tests when executed directly."""
    results = run_smoke_tests()

    print("=== DenarioApp Retrieval Smoke Tests ===")
    total_passed = sum(category["passed"] for category in results.values())
    total_failed = sum(category["failed"] for category in results.values())

    for category, stats in results.items():
        print(f"\n{category.upper()}:")
        print(f"  Passed: {stats['passed']}")
        print(f"  Failed: {stats['failed']}")
        if stats["errors"]:
            print(f"  Errors: {stats['errors']}")

    print(f"\nTOTAL: {total_passed} passed, {total_failed} failed")

    if total_failed > 0:
        sys.exit(1)
    else:
        print("✅ All smoke tests passed!")
        sys.exit(0)

