"""
arXiv integration for academic paper retrieval.
This module provides arXiv search functionality for DenarioApp.
"""

import os
import json
import logging
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)


class ArxivRetriever:
    """arXiv API retriever for academic papers."""

    def __init__(self, max_results: int = 10):
        self.base_url = "http://export.arxiv.org/api/query"
        self.max_results = max_results

    def _parse_arxiv_entry(self, entry) -> Dict[str, Any]:
        """Parse an arXiv API entry into a structured format."""
        # Extract basic information
        title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
        summary = entry.find(
            '{http://www.w3.org/2005/Atom}summary').text.strip()
        published = entry.find('{http://www.w3.org/2005/Atom}published').text
        updated = entry.find('{http://www.w3.org/2005/Atom}updated').text

        # Extract authors
        authors = []
        for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
            name = author.find('{http://www.w3.org/2005/Atom}name').text
            authors.append(name)

        # Extract arXiv ID and links
        arxiv_id = None
        pdf_url = None
        abstract_url = None

        for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
            if link.get('type') == 'application/pdf':
                pdf_url = link.get('href')
            elif link.get('type') == 'text/html':
                abstract_url = link.get('href')

        # Extract arXiv ID from the abstract URL
        if abstract_url:
            match = re.search(r'abs/(\d+\.\d+(?:v\d+)?)', abstract_url)
            if match:
                arxiv_id = match.group(1)

        # Extract categories
        categories = []
        for category in entry.findall('{http://www.w3.org/2005/Atom}category'):
            term = category.get('term')
            if term:
                categories.append(term)

        # Generate DOI if not present (arXiv papers often don't have DOIs)
        doi = None
        if arxiv_id:
            doi = f"10.48550/arXiv.{arxiv_id}"

        return {
            "title": title,
            "authors": authors,
            "summary": summary,
            "published": published,
            "updated": updated,
            "arxiv_id": arxiv_id,
            "pdf_url": pdf_url,
            "abstract_url": abstract_url,
            "doi": doi,
            "categories": categories,
            "type": "arxiv_paper"
        }

    def search(self, query: str,
               max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search arXiv for papers matching the query."""
        if max_results is None:
            max_results = self.max_results

        # Construct search parameters
        params = {
            'search_query': query,
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }

        try:
            logger.info(f"Searching arXiv for: {query}")
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()

            # Parse XML response
            root = ET.fromstring(response.content)

            # Extract entries
            entries = root.findall('{http://www.w3.org/2005/Atom}entry')
            results = []

            for entry in entries:
                paper = self._parse_arxiv_entry(entry)
                results.append(paper)

            logger.info(f"Found {len(results)} papers from arXiv")
            return results

        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
            return []

    def search_by_category(
            self, category: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search arXiv by category."""
        if max_results is None:
            max_results = self.max_results

        # Common arXiv categories for cosmology/physics
        category_map = {
            "cosmology": "astro-ph.CO",
            "astrophysics": "astro-ph",
            "physics": "physics",
            "general relativity": "gr-qc",
            "particle physics": "hep-ph",
            "quantum field theory": "hep-th"
        }

        arxiv_category = category_map.get(category.lower(), category)
        query = f"cat:{arxiv_category}"

        return self.search(query, max_results)

    def get_recent_papers(self,
                          category: str = "astro-ph.CO",
                          days: int = 30,
                          max_results: Optional[int] = None) -> List[Dict[str,
                                                                          Any]]:
        """Get recent papers from a specific category."""
        if max_results is None:
            max_results = self.max_results

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Format dates for arXiv API
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")

        query = f"cat:{category} AND submittedDate:[{start_str}0000 TO {end_str}2359]"

        return self.search(query, max_results)

    def format_for_denario(self, papers: List[Dict[str, Any]]) -> str:
        """Format arXiv papers for DenarioApp display."""
        if not papers:
            return "No papers found."

        result = f"Found {len(papers)} relevant papers from arXiv:\n\n"

        for i, paper in enumerate(papers, 1):
            result += f"{i}. {paper['title']}\n"
            result += f"   Authors: {', '.join(paper['authors'][:3])}"
            if len(paper['authors']) > 3:
                result += f" et al. ({len(paper['authors'])} total)"
            result += "\n"

            if paper['arxiv_id']:
                result += f"   arXiv ID: {paper['arxiv_id']}\n"

            if paper['doi']:
                result += f"   DOI: https://doi.org/{paper['doi']}\n"

            if paper['categories']:
                result += f"   Categories: {', '.join(paper['categories'][:2])}\n"

            if paper['abstract_url']:
                result += f"   URL: {paper['abstract_url']}\n"

            # Add summary preview
            summary = paper['summary'][:200] + \
                "..." if len(paper['summary']) > 200 else paper['summary']
            result += f"   Abstract: {summary}\n"
            result += "\n"

        return result


class ArxivRAGRetriever:
    """arXiv RAG retriever for DenarioApp integration."""

    def __init__(self, max_results: int = 5):
        self.retriever = ArxivRetriever(max_results)

    def retrieve(self, query: str,
                 max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant papers for a query."""
        papers = self.retriever.search(query, max_results)

        # Format for DenarioApp
        formatted_results = []
        for paper in papers:
            formatted_results.append({
                "title": paper["title"],
                "url": paper["abstract_url"] or f"https://arxiv.org/abs/{paper['arxiv_id']}",
                "doi": paper["doi"],
                "content": paper["summary"],
                "authors": paper["authors"],
                "arxiv_id": paper["arxiv_id"],
                "categories": paper["categories"],
                "published": paper["published"],
                "type": "arxiv_paper"
            })

        return formatted_results

    def search_by_topic(
            self,
            topic: str,
            max_results: Optional[int] = None) -> str:
        """Search by topic and return formatted results."""
        papers = self.retriever.search(topic, max_results)
        return self.retriever.format_for_denario(papers)

    def get_recent_cosmology_papers(
            self,
            days: int = 30,
            max_results: Optional[int] = None) -> str:
        """Get recent cosmology papers."""
        papers = self.retriever.get_recent_papers(
            "astro-ph.CO", days, max_results)
        return self.retriever.format_for_denario(papers)


# Global instance for easy access
_arxiv_retriever = None


def get_arxiv_retriever() -> ArxivRAGRetriever:
    """Get the global arXiv retriever instance."""
    global _arxiv_retriever
    if _arxiv_retriever is None:
        _arxiv_retriever = ArxivRAGRetriever()
    return _arxiv_retriever
