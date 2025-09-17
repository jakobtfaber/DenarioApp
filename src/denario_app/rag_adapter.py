"""
Unified RAG Adapter Interface for DenarioApp.
Provides a consistent interface for all retrieval providers with graceful fallbacks.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class RAGProvider(Enum):
    """Enumeration of available RAG providers."""
    PERPLEXITY = "Perplexity (web)"
    DOMAIN = "Domain (Planck/CAMB/CLASSY)"
    GRAPHRAG = "GraphRAG (local corpus)"
    ARXIV = "arXiv (academic papers)"


@dataclass
class RetrievalResult:
    """Standardized result format for all RAG providers."""
    title: str
    url: str
    doi: Optional[str] = None
    content: str = ""
    score: float = 0.0
    provider: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RAGAdapter(ABC):
    """Abstract base class for RAG adapters."""

    @abstractmethod
    def retrieve(
            self,
            query: str,
            max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve relevant documents for a query."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the human-readable provider name."""
        pass


class PerplexityAdapter(RAGAdapter):
    """Adapter for Perplexity web search."""

    def __init__(self):
        self.provider_name = RAGProvider.PERPLEXITY.value
        self.api_key = os.getenv("PERPLEXITY_API_KEY")

    def is_available(self) -> bool:
        """Check if Perplexity API key is available."""
        return self.api_key is not None

    def get_provider_name(self) -> str:
        return self.provider_name

    def retrieve(
            self,
            query: str,
            max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve results from Perplexity (fallback to domain context)."""
        if not self.is_available():
            logger.warning("Perplexity API key not available, using fallback")
            return self._fallback_retrieve(query, max_results)

        try:
            # For now, return domain context as fallback
            # In a full implementation, this would call Perplexity API
            return self._fallback_retrieve(query, max_results)
        except Exception as e:
            logger.error(f"Perplexity retrieval failed: {e}")
            return self._fallback_retrieve(query, max_results)

    def _fallback_retrieve(
            self,
            query: str,
            max_results: int) -> List[RetrievalResult]:
        """Fallback to domain context when Perplexity is unavailable."""
        return [
            RetrievalResult(
                title="Web Search Fallback",
                url="https://perplexity.ai",
                content=f"Perplexity search for: {query}",
                score=1.0,
                provider=self.provider_name,
                metadata={"fallback": True, "query": query}
            )
        ]


class DomainAdapter(RAGAdapter):
    """Adapter for domain-specific context (Planck/CAMB/CLASSY)."""

    def __init__(self):
        self.provider_name = RAGProvider.DOMAIN.value

    def is_available(self) -> bool:
        """Domain context is always available."""
        return True

    def get_provider_name(self) -> str:
        return self.provider_name

    def retrieve(
            self,
            query: str,
            max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve domain-specific context."""
        domain_contexts = self._get_domain_contexts()

        results = []
        for context in domain_contexts[:max_results]:
            results.append(RetrievalResult(
                title=context["title"],
                url=context["url"],
                content=context["content"],
                score=1.0,
                provider=self.provider_name,
                metadata=context.get("metadata", {})
            ))

        return results

    def _get_domain_contexts(self) -> List[Dict[str, Any]]:
        """Get domain-specific context information."""
        return [{"title": "Planck Mission Context",
                 "url": "https://www.cosmos.esa.int/web/planck",
                 "content": """Planck 2018 results: cosmological parameters from CMB temperature and polarization
- Key datasets: Planck 2018 TT,TE,EE+lowE+lensing+BAO
- Relevant parameters: H0, Ωm, ΩΛ, ns, As, τ
- Recent constraints: H0 = 67.4 ± 0.5 km/s/Mpc (Planck 2018)
- Lensing potential: Planck lensing reconstruction
- Systematics: foreground contamination, beam uncertainties""",
                 "metadata": {"domain": "planck",
                              "type": "mission_context"}},
                {"title": "CAMB (Code for Anisotropies in the Microwave Background)",
                 "url": "https://camb.readthedocs.io/",
                 "content": """Boltzmann solver for CMB anisotropies and matter power spectra
- Key features: scalar, vector, tensor modes; dark energy models
- Recent updates: CAMB 1.3+ with improved precision
- Applications: parameter estimation, likelihood analysis
- Integration: CosmoMC, MontePython, Cobaya
- Outputs: Cl, P(k), transfer functions""",
                 "metadata": {"domain": "camb",
                              "type": "tool_context"}},
                {"title": "CLASSY (Cosmic Linear Anisotropy Solving System)",
                 "url": "https://class-code.net/",
                 "content": """Alternative to CAMB for CMB and LSS calculations
- Features: high precision, modular design, dark energy models
- Recent work: CLASSY-SZ for Sunyaev-Zel'dovich effects
- Applications: parameter estimation, model comparison
- Integration: MontePython, Cobaya
- Advantages: speed, flexibility, extended models""",
                 "metadata": {"domain": "classy",
                              "type": "tool_context"}}]


class GraphRAGAdapter(RAGAdapter):
    """Adapter for GraphRAG local corpus search."""

    def __init__(self):
        self.provider_name = RAGProvider.GRAPHRAG.value
        self._retriever = None

    def is_available(self) -> bool:
        """Check if GraphRAG is available."""
        try:
            from .graphrag import get_graphrag_retriever
            return True
        except ImportError:
            return False

    def get_provider_name(self) -> str:
        return self.provider_name

    def retrieve(
            self,
            query: str,
            max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve results from GraphRAG."""
        if not self.is_available():
            logger.warning("GraphRAG not available")
            return []

        try:
            if self._retriever is None:
                from .graphrag import get_graphrag_retriever
                self._retriever = get_graphrag_retriever()

            results = self._retriever.retrieve(query, max_results)

            # Convert to standard format
            retrieval_results = []
            for result in results:
                retrieval_results.append(RetrievalResult(
                    title=result["title"],
                    url=result["url"],
                    doi=result.get("doi"),
                    content=result["content"],
                    score=result.get("score", 0.0),
                    provider=self.provider_name,
                    metadata=result.get("metadata", {})
                ))

            return retrieval_results

        except Exception as e:
            logger.error(f"GraphRAG retrieval failed: {e}")
            return []

    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get corpus statistics."""
        if not self.is_available() or self._retriever is None:
            return {"documents": 0, "entities": 0, "relationships": 0}

        try:
            return self._retriever.get_corpus_stats()
        except Exception as e:
            logger.error(f"Failed to get corpus stats: {e}")
            return {"documents": 0, "entities": 0, "relationships": 0}


class ArxivAdapter(RAGAdapter):
    """Adapter for arXiv academic paper search."""

    def __init__(self):
        self.provider_name = RAGProvider.ARXIV.value
        self._retriever = None

    def is_available(self) -> bool:
        """Check if arXiv adapter is available."""
        try:
            from .arxiv_rag import get_arxiv_retriever
            return True
        except ImportError:
            return False

    def get_provider_name(self) -> str:
        return self.provider_name

    def retrieve(
            self,
            query: str,
            max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve results from arXiv."""
        if not self.is_available():
            logger.warning("arXiv adapter not available")
            return []

        try:
            if self._retriever is None:
                from .arxiv_rag import get_arxiv_retriever
                self._retriever = get_arxiv_retriever()

            results = self._retriever.retrieve(query, max_results)

            # Convert to standard format
            retrieval_results = []
            for result in results:
                retrieval_results.append(RetrievalResult(
                    title=result["title"],
                    url=result["url"],
                    doi=result.get("doi"),
                    content=result["content"],
                    score=1.0,  # arXiv doesn't provide scores
                    provider=self.provider_name,
                    metadata={
                        "authors": result.get("authors", []),
                        "arxiv_id": result.get("arxiv_id"),
                        "categories": result.get("categories", []),
                        "published": result.get("published"),
                        "type": "arxiv_paper"
                    }
                ))

            return retrieval_results

        except Exception as e:
            logger.error(f"arXiv retrieval failed: {e}")
            return []


class UnifiedRAGAdapter:
    """Unified interface for all RAG providers with graceful fallbacks."""

    def __init__(self):
        self.adapters = {
            RAGProvider.PERPLEXITY: PerplexityAdapter(),
            RAGProvider.DOMAIN: DomainAdapter(),
            RAGProvider.GRAPHRAG: GraphRAGAdapter(),
            RAGProvider.ARXIV: ArxivAdapter(),
        }

    def get_available_providers(self) -> List[RAGProvider]:
        """Get list of available providers."""
        available = []
        for provider, adapter in self.adapters.items():
            if adapter.is_available():
                available.append(provider)
        return available

    def retrieve(self, query: str, provider: Union[RAGProvider, str],
                 max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve results from specified provider."""
        if isinstance(provider, str):
            # Convert string to enum
            try:
                provider = RAGProvider(provider)
            except ValueError:
                logger.error(f"Unknown provider: {provider}")
                return []

        if provider not in self.adapters:
            logger.error(f"Provider not configured: {provider}")
            return []

        adapter = self.adapters[provider]

        if not adapter.is_available():
            logger.warning(f"Provider {provider.value} not available")
            return []

        try:
            return adapter.retrieve(query, max_results)
        except Exception as e:
            logger.error(f"Retrieval failed for {provider.value}: {e}")
            return []

    def retrieve_with_fallback(self,
                               query: str,
                               preferred_provider: Union[RAGProvider,
                                                         str],
                               max_results: int = 5) -> List[RetrievalResult]:
        """Retrieve with fallback to other providers if preferred fails."""
        if isinstance(preferred_provider, str):
            try:
                preferred_provider = RAGProvider(preferred_provider)
            except ValueError:
                logger.error(f"Unknown provider: {preferred_provider}")
                return []

        # Try preferred provider first
        results = self.retrieve(query, preferred_provider, max_results)
        if results:
            return results

        # Fallback to other available providers
        available_providers = self.get_available_providers()
        for provider in available_providers:
            if provider != preferred_provider:
                results = self.retrieve(query, provider, max_results)
                if results:
                    logger.info(f"Using fallback provider: {provider.value}")
                    return results

        logger.warning("All providers failed or unavailable")
        return []

    def get_provider_info(
            self, provider: Union[RAGProvider, str]) -> Dict[str, Any]:
        """Get information about a specific provider."""
        if isinstance(provider, str):
            try:
                provider = RAGProvider(provider)
            except ValueError:
                return {"error": f"Unknown provider: {provider}"}

        if provider not in self.adapters:
            return {"error": f"Provider not configured: {provider}"}

        adapter = self.adapters[provider]
        info = {
            "name": adapter.get_provider_name(),
            "available": adapter.is_available(),
            "provider": provider.value
        }

        # Add provider-specific info
        if provider == RAGProvider.GRAPHRAG and hasattr(
                adapter, 'get_corpus_stats'):
            info["corpus_stats"] = adapter.get_corpus_stats()

        return info

    def get_all_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all providers."""
        info = {}
        for provider in RAGProvider:
            info[provider.value] = self.get_provider_info(provider)
        return info


# Global instance for easy access
_unified_adapter = None


def get_unified_rag_adapter() -> UnifiedRAGAdapter:
    """Get the global unified RAG adapter instance."""
    global _unified_adapter
    if _unified_adapter is None:
        _unified_adapter = UnifiedRAGAdapter()
    return _unified_adapter


def format_results_for_ui(results: List[RetrievalResult]) -> str:
    """Format retrieval results for UI display."""
    if not results:
        return "No results found."

    formatted = f"Found {len(results)} relevant documents:\n\n"

    for i, result in enumerate(results, 1):
        formatted += f"{i}. {result.title}\n"

        if result.doi:
            formatted += f"   DOI: https://doi.org/{result.doi}\n"

        if result.url:
            formatted += f"   URL: {result.url}\n"

        if result.metadata.get("authors"):
            authors = result.metadata["authors"][:3]
            formatted += f"   Authors: {', '.join(authors)}"
            if len(result.metadata["authors"]) > 3:
                formatted += f" et al. ({len(result.metadata['authors'])} total)"
            formatted += "\n"

        if result.metadata.get("categories"):
            formatted += f"   Categories: {', '.join(result.metadata['categories'][:2])}\n"

        if result.content:
            content_preview = result.content[:200] + \
                "..." if len(result.content) > 200 else result.content
            formatted += f"   Content: {content_preview}\n"

        formatted += f"   Provider: {result.provider}\n"
        formatted += "\n"

    return formatted

