"""
GraphRAG implementation for local corpus indexing and retrieval.
This module provides a simple GraphRAG implementation for indexing
and querying the local ragbook corpus.
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
import re

logger = logging.getLogger(__name__)


class GraphRAGIndexer:
    """Simple GraphRAG indexer for local corpus."""

    def __init__(self, corpus_path: str = "/data/cmbagents/ragbook",
                 index_path: str = "/data/cmbagents/ragbook/graphrag_index"):
        self.corpus_path = Path(corpus_path)
        self.index_path = Path(index_path)
        self.index_path.mkdir(exist_ok=True)

        # Index files
        self.documents_file = self.index_path / "documents.json"
        self.entities_file = self.index_path / "entities.json"
        self.relationships_file = self.index_path / "relationships.json"

        # Load existing index
        self.documents = self._load_json(self.documents_file, {})
        self.entities = self._load_json(self.entities_file, {})
        self.relationships = self._load_json(self.relationships_file, {})

    def _load_json(self, file_path: Path, default: Any) -> Any:
        """Load JSON file or return default if not found."""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
        return default

    def _save_json(self, data: Any, file_path: Path) -> None:
        """Save data to JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")

    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text using simple patterns."""
        entities = []

        # Extract DOIs
        doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Za-z0-9]+'
        dois = re.findall(doi_pattern, text)
        entities.extend([f"doi:{doi}" for doi in dois])

        # Extract arXiv IDs
        arxiv_pattern = r'\d{4}\.\d{4,5}(?:v\d+)?'
        arxiv_ids = re.findall(arxiv_pattern, text)
        entities.extend([f"arxiv:{arxiv_id}" for arxiv_id in arxiv_ids])

        # Extract author names (simple pattern)
        author_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        authors = re.findall(author_pattern, text)
        # Limit to 10
        entities.extend([f"author:{author}" for author in authors[:10]])

        # Extract technical terms
        tech_terms = [
            'cosmology', 'CMB', 'Planck', 'CAMB', 'CLASS', 'CLASSY',
            'dark matter', 'dark energy', 'baryon acoustic oscillations',
            'redshift', 'luminosity distance', 'angular diameter distance',
            'power spectrum', 'correlation function', 'galaxy clustering',
            'weak lensing', 'strong lensing', 'gravitational waves',
            'inflation', 'reionization', 'baryogenesis'
        ]

        for term in tech_terms:
            if term.lower() in text.lower():
                entities.append(f"concept:{term}")

        return list(set(entities))  # Remove duplicates

    def _extract_relationships(
            self, text: str, entities: List[str]) -> List[Dict[str, str]]:
        """Extract relationships between entities."""
        relationships = []

        # Simple co-occurrence relationships
        for i, entity1 in enumerate(entities):
            for entity2 in entities[i + 1:]:
                if self._entities_co_occur(text, entity1, entity2):
                    relationships.append({
                        "source": entity1,
                        "target": entity2,
                        "type": "co_occurs_with",
                        "strength": 1.0
                    })

        return relationships

    def _entities_co_occur(
            self,
            text: str,
            entity1: str,
            entity2: str) -> bool:
        """Check if two entities co-occur in the text."""
        # Extract the actual term from entity (remove prefix)
        term1 = entity1.split(':', 1)[1] if ':' in entity1 else entity1
        term2 = entity2.split(':', 1)[1] if ':' in entity2 else entity2

        # Check if both terms appear in the same sentence or within 100
        # characters
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            if term1.lower() in sentence.lower() and term2.lower() in sentence.lower():
                return True

        # Also check within 100 characters
        for i in range(len(text) - 100):
            chunk = text[i:i + 100]
            if term1.lower() in chunk.lower() and term2.lower() in chunk.lower():
                return True

        return False

    def _process_document(self, file_path: Path) -> Dict[str, Any]:
        """Process a single document and extract information."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Failed to read {file_path}: {e}")
            return None

        # Generate document ID
        doc_id = hashlib.md5(str(file_path).encode()).hexdigest()[:16]

        # Extract entities and relationships
        entities = self._extract_entities(content)
        relationships = self._extract_relationships(content, entities)

        document = {
            "id": doc_id,
            "path": str(file_path),
            "filename": file_path.name,
            "content": content[:1000],  # First 1000 chars for preview
            "entities": entities,
            "relationships": relationships,
            "size": len(content),
            "type": file_path.suffix
        }

        return document

    def index_corpus(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """Index the entire corpus."""
        if not force_rebuild and self.documents:
            logger.info("Index already exists, skipping rebuild")
            return {"status": "skipped", "documents": len(self.documents)}

        logger.info(f"Indexing corpus at {self.corpus_path}")

        # Find all relevant files
        file_patterns = ['*.jsonl', '*.md', '*.tex', '*.txt']
        files_to_process = []

        for pattern in file_patterns:
            files_to_process.extend(self.corpus_path.rglob(pattern))

        # Filter out very large files and system files
        files_to_process = [
            f for f in files_to_process
            if f.stat().st_size < 10 * 1024 * 1024 and  # < 10MB
            not any(part.startswith('.') for part in f.parts) and
            not f.name.startswith('.')
        ]

        logger.info(f"Found {len(files_to_process)} files to process")

        # Process documents
        new_documents = {}
        all_entities = {}
        all_relationships = []

        for file_path in files_to_process:
            doc = self._process_document(file_path)
            if doc:
                new_documents[doc["id"]] = doc

                # Update entity index
                for entity in doc["entities"]:
                    if entity not in all_entities:
                        all_entities[entity] = []
                    all_entities[entity].append(doc["id"])

                # Add relationships
                all_relationships.extend(doc["relationships"])

        # Save index
        self.documents = new_documents
        self.entities = all_entities
        self.relationships = all_relationships

        self._save_json(self.documents, self.documents_file)
        self._save_json(self.entities, self.entities_file)
        self._save_json(self.relationships, self.relationships_file)

        logger.info(
            f"Indexed {
                len(new_documents)} documents, {
                len(all_entities)} entities, {
                len(all_relationships)} relationships")

        return {
            "status": "success",
            "documents": len(new_documents),
            "entities": len(all_entities),
            "relationships": len(all_relationships)
        }

    def search(self, query: str,
               max_results: int = 10) -> List[Dict[str, Any]]:
        """Search the indexed corpus."""
        if not self.documents:
            logger.warning("No documents indexed, run index_corpus() first")
            return []

        query_lower = query.lower()
        results = []

        for doc_id, doc in self.documents.items():
            score = 0

            # Text content matching
            if query_lower in doc["content"].lower():
                score += 2

            # Entity matching
            for entity in doc["entities"]:
                if query_lower in entity.lower():
                    score += 1

            # Filename matching
            if query_lower in doc["filename"].lower():
                score += 1

            if score > 0:
                results.append({
                    "document": doc,
                    "score": score,
                    "matches": self._get_match_context(doc, query)
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def _get_match_context(self, doc: Dict[str, Any], query: str) -> List[str]:
        """Get context around matches in the document."""
        content = doc["content"]
        query_lower = query.lower()
        matches = []

        # Find all occurrences
        start = 0
        while True:
            pos = content.lower().find(query_lower, start)
            if pos == -1:
                break

            # Extract context around match
            context_start = max(0, pos - 100)
            context_end = min(len(content), pos + len(query) + 100)
            context = content[context_start:context_end]

            matches.append(context.strip())
            start = pos + 1

            if len(matches) >= 3:  # Limit to 3 matches
                break

        return matches

    def get_entity_info(self, entity: str) -> Dict[str, Any]:
        """Get information about a specific entity."""
        if entity not in self.entities:
            return {"entity": entity, "documents": [], "relationships": []}

        doc_ids = self.entities[entity]
        documents = [self.documents[doc_id]
                     for doc_id in doc_ids if doc_id in self.documents]

        # Find relationships involving this entity
        entity_relationships = [
            rel for rel in self.relationships
            if rel["source"] == entity or rel["target"] == entity
        ]

        return {
            "entity": entity,
            "documents": documents,
            "relationships": entity_relationships,
            "document_count": len(documents)
        }


class GraphRAGRetriever:
    """GraphRAG-based retriever for DenarioApp integration."""

    def __init__(self, indexer: Optional[GraphRAGIndexer] = None):
        self.indexer = indexer or GraphRAGIndexer()
        self._ensure_indexed()

    def _ensure_indexed(self):
        """Ensure the corpus is indexed."""
        if not self.indexer.documents:
            logger.info("No index found, building GraphRAG index...")
            self.indexer.index_corpus()

    def retrieve(self, query: str,
                 max_results: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query."""
        results = self.indexer.search(query, max_results)

        # Format results for DenarioApp
        formatted_results = []
        for result in results:
            doc = result["document"]
            formatted_results.append({
                "title": doc["filename"],
                "url": f"file://{doc['path']}",
                "doi": None,  # Extract DOI if present
                "content": doc["content"],
                "score": result["score"],
                "matches": result["matches"],
                "entities": doc["entities"][:5],  # Top 5 entities
                "type": "local_corpus"
            })

        return formatted_results

    def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed corpus."""
        return {
            "documents": len(self.indexer.documents),
            "entities": len(self.indexer.entities),
            "relationships": len(self.indexer.relationships),
            "corpus_path": str(self.indexer.corpus_path)
        }


# Global instance for easy access
_graphrag_retriever = None


def get_graphrag_retriever() -> GraphRAGRetriever:
    """Get the global GraphRAG retriever instance."""
    global _graphrag_retriever
    if _graphrag_retriever is None:
        _graphrag_retriever = GraphRAGRetriever()
    return _graphrag_retriever
