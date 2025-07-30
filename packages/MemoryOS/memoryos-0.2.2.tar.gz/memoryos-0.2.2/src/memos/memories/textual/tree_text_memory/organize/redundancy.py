import json
import re

from datetime import datetime

from memos.embedders.base import BaseEmbedder
from memos.graph_dbs.neo4j import Neo4jGraphDB
from memos.llms.base import BaseLLM
from memos.log import get_logger
from memos.memories.textual.item import TextualMemoryItem, TreeNodeTextualMemoryMetadata
from memos.templates.tree_reorganize_prompts import (
    REDUNDANCY_DETECTOR_PROMPT,
    REDUNDANCY_MERGE_PROMPT,
    REDUNDANCY_RESOLVER_PROMPT,
)


logger = get_logger(__name__)


class RedundancyHandler:
    EMBEDDING_THRESHOLD: float = 0.8  # Threshold for embedding similarity to consider redundancy

    def __init__(self, graph_store: Neo4jGraphDB, llm: BaseLLM, embedder: BaseEmbedder):
        self.graph_store = graph_store
        self.llm = llm
        self.embedder = embedder

    def detect(
        self, memory: TextualMemoryItem, top_k: int = 5, scope: str | None = None
    ) -> list[tuple[TextualMemoryItem, TextualMemoryItem]]:
        """
        Detect redundancy by finding the most similar items in the graph database based on embedding, then use LLM to judge redundancy.
        Args:
            memory: The memory item (should have an embedding attribute or field).
            top_k: Number of top similar nodes to retrieve.
            scope: Optional memory type filter.
        Returns:
            List of redundancy pairs (each pair is a tuple: (memory, candidate)).
        """
        # 1. Search for similar memories based on embedding
        embedding = memory.metadata.embedding
        embedding_candidates_info = self.graph_store.search_by_embedding(
            embedding, top_k=top_k, scope=scope
        )
        # 2. Filter based on similarity threshold
        embedding_candidates_ids = [
            info["id"]
            for info in embedding_candidates_info
            if info["score"] >= self.EMBEDDING_THRESHOLD and info["id"] != memory.id
        ]
        # 3. Judge redundancys using LLM
        embedding_candidates = self.graph_store.get_nodes(embedding_candidates_ids)
        redundant_pairs = []
        for embedding_candidate in embedding_candidates:
            embedding_candidate = TextualMemoryItem.from_dict(embedding_candidate)
            prompt = [
                {
                    "role": "system",
                    "content": "You are a redundancy detector for memory items.",
                },
                {
                    "role": "user",
                    "content": REDUNDANCY_DETECTOR_PROMPT.format(
                        statement_1=memory.memory,
                        statement_2=embedding_candidate.memory,
                    ),
                },
            ]
            result = self.llm.generate(prompt).strip()
            if "yes" in result.lower():
                redundant_pairs.append([memory, embedding_candidate])
        if len(redundant_pairs):
            redundant_text = "\n".join(
                f'"{pair[0].memory!s}" <==REDUNDANCY==> "{pair[1].memory!s}"'
                for pair in redundant_pairs
            )
            logger.warning(
                f"Detected {len(redundant_pairs)} redundancies for memory {memory.id}\n {redundant_text}"
            )
        return redundant_pairs

    def resolve_two_nodes(self, memory_a: TextualMemoryItem, memory_b: TextualMemoryItem) -> None:
        """
        Resolve detected redundancies between two memory items using LLM fusion.
        Args:
            memory_a: The first redundant memory item.
            memory_b: The second redundant memory item.
        Returns:
            A fused TextualMemoryItem representing the resolved memory.
        """
        return  # waiting for implementation
        # ———————————— 1. LLM generate fused memory ————————————
        metadata_for_resolve = ["key", "background", "confidence", "updated_at"]
        metadata_1 = memory_a.metadata.model_dump_json(include=metadata_for_resolve)
        metadata_2 = memory_b.metadata.model_dump_json(include=metadata_for_resolve)
        prompt = [
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "user",
                "content": REDUNDANCY_RESOLVER_PROMPT.format(
                    statement_1=memory_a.memory,
                    metadata_1=metadata_1,
                    statement_2=memory_b.memory,
                    metadata_2=metadata_2,
                ),
            },
        ]
        response = self.llm.generate(prompt).strip()

        # ———————————— 2. Parse the response ————————————
        try:
            answer = re.search(r"<answer>(.*?)</answer>", response, re.DOTALL)
            answer = answer.group(1).strip()
            fixed_metadata = self._merge_metadata(answer, memory_a.metadata, memory_b.metadata)
            merged_memory = TextualMemoryItem(memory=answer, metadata=fixed_metadata)
            logger.info(f"Resolved result: {merged_memory}")
            self._resolve_in_graph(memory_a, memory_b, merged_memory)
        except json.decoder.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response}")

    def resolve_one_node(self, memory: TextualMemoryItem) -> None:
        prompt = [
            {
                "role": "user",
                "content": REDUNDANCY_MERGE_PROMPT.format(merged_text=memory.memory),
            },
        ]
        response = self.llm.generate(prompt)
        memory.memory = response.strip()
        self.graph_store.update_node(
            memory.id,
            {"memory": memory.memory, **memory.metadata.model_dump(exclude_none=True)},
        )
        logger.debug(f"Merged memory: {memory.memory}")

    def _resolve_in_graph(
        self,
        redundant_a: TextualMemoryItem,
        redundant_b: TextualMemoryItem,
        merged: TextualMemoryItem,
    ):
        edges_a = self.graph_store.get_edges(redundant_a.id, type="ANY", direction="ANY")
        edges_b = self.graph_store.get_edges(redundant_b.id, type="ANY", direction="ANY")
        all_edges = edges_a + edges_b

        self.graph_store.add_node(
            merged.id, merged.memory, merged.metadata.model_dump(exclude_none=True)
        )

        for edge in all_edges:
            new_from = (
                merged.id if edge["from"] in (redundant_a.id, redundant_b.id) else edge["from"]
            )
            new_to = merged.id if edge["to"] in (redundant_a.id, redundant_b.id) else edge["to"]
            if new_from == new_to:
                continue
            # Check if the edge already exists before adding
            if not self.graph_store.edge_exists(new_from, new_to, edge["type"], direction="ANY"):
                self.graph_store.add_edge(new_from, new_to, edge["type"])

        self.graph_store.update_node(redundant_a.id, {"status": "archived"})
        self.graph_store.update_node(redundant_b.id, {"status": "archived"})
        self.graph_store.add_edge(redundant_a.id, merged.id, type="MERGED_TO")
        self.graph_store.add_edge(redundant_b.id, merged.id, type="MERGED_TO")
        logger.debug(
            f"Archive {redundant_a.id} and {redundant_b.id}, and inherit their edges to {merged.id}."
        )

    def _merge_metadata(
        self,
        memory: str,
        metadata_a: TreeNodeTextualMemoryMetadata,
        metadata_b: TreeNodeTextualMemoryMetadata,
    ) -> TreeNodeTextualMemoryMetadata:
        metadata_1 = metadata_a.model_dump()
        metadata_2 = metadata_b.model_dump()
        merged_metadata = {
            "sources": (metadata_1["sources"] or []) + (metadata_2["sources"] or []),
            "embedding": self.embedder.embed([memory])[0],
            "update_at": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
        }
        for key in metadata_1:
            if key in merged_metadata:
                continue
            merged_metadata[key] = (
                metadata_1[key] if metadata_1[key] is not None else metadata_2[key]
            )
        return TreeNodeTextualMemoryMetadata.model_validate(merged_metadata)
