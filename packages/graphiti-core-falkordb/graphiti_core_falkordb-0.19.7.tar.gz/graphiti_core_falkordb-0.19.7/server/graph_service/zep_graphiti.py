import logging
from typing import Annotated, Optional, Dict, List

from fastapi import Depends, HTTPException
from graphiti_core_falkordb import Graphiti  # type: ignore
from graphiti_core_falkordb.edges import EntityEdge  # type: ignore
from graphiti_core_falkordb.embedder.voyage import VoyageAIEmbedder
from graphiti_core_falkordb.errors import EdgeNotFoundError, GroupsEdgesNotFoundError, NodeNotFoundError
from graphiti_core_falkordb.llm_client import LLMClient  # type: ignore
from graphiti_core_falkordb.nodes import EntityNode, EpisodicNode  # type: ignore
from graphiti_core_falkordb.driver.falkordb_driver import FalkorDriver
from graph_service.config import ZepEnvDep
from graph_service.dto import FactResult
import os
logger = logging.getLogger(__name__)
from dotenv import load_dotenv





load_dotenv()
# Global instance for initialization
_global_graphiti_instance: Optional['ZepGraphiti'] = None




FALKORDB_HOST = os.getenv('FALKORDB_HOST', 'falkordb')
FALKORDB_PORT = os.getenv('FALKORDB_PORT', '6379')
FALKORDB_USER = os.getenv('FALKORDB_USER', None)
FALKORDB_PASSWORD = os.getenv('FALKORDB_PASSWORD', None)

class ZepGraphiti(Graphiti):
    def __init__(self, llm_client: LLMClient | None = None):
        try:
            # Try new constructor signature
            driver = FalkorDriver(host=FALKORDB_HOST, port=FALKORDB_PORT, username=FALKORDB_USER, password=FALKORDB_PASSWORD)
        except TypeError:
            # Fall back to old constructor signature that requires uri, user, password
            falkor_uri = f"redis://{FALKORDB_USER or 'default'}:{FALKORDB_PASSWORD or 'password'}@{FALKORDB_HOST}:{FALKORDB_PORT}"
            driver = FalkorDriver(falkor_uri, FALKORDB_USER or 'default', FALKORDB_PASSWORD or 'password')
        super().__init__(llm_client=llm_client, embedder=VoyageAIEmbedder(), graph_driver=driver)

    async def save_entity_node(self, name: str, uuid: str, group_id: str, summary: str = '',
                              labels: Optional[List[str]] = None, attributes: Optional[Dict] = None,
                              extra_attributes: Optional[Dict] = None):
        new_node = EntityNode(
            name=name,
            uuid=uuid,
            group_id=group_id,
            summary=summary,
            labels=labels or [],
            attributes=attributes or {},
            extra_attributes=extra_attributes or {},
        )
        await new_node.generate_name_embedding(self.embedder)
        await new_node.save(self.driver)
        return new_node

    async def get_entity_edge(self, uuid: str):
        try:
            edge = await EntityEdge.get_by_uuid(self.driver, uuid)
            return edge
        except EdgeNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.message) from e

    async def delete_group(self, group_id: str):
        try:
            edges = await EntityEdge.get_by_group_ids(self.driver, [group_id])
        except GroupsEdgesNotFoundError:
            logger.warning(f'No edges found for group {group_id}')
            edges = []

        nodes = await EntityNode.get_by_group_ids(self.driver, [group_id])

        episodes = await EpisodicNode.get_by_group_ids(self.driver, [group_id])

        for edge in edges:
            await edge.delete(self.driver)

        for node in nodes:
            await node.delete(self.driver)

        for episode in episodes:
            await episode.delete(self.driver)

    async def delete_entity_edge(self, uuid: str):
        try:
            edge = await EntityEdge.get_by_uuid(self.driver, uuid)
            await edge.delete(self.driver)
        except EdgeNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.message) from e

    async def delete_episodic_node(self, uuid: str):
        try:
            episode = await EpisodicNode.get_by_uuid(self.driver, uuid)
            await episode.delete(self.driver)
        except NodeNotFoundError as e:
            raise HTTPException(status_code=404, detail=e.message) from e


async def get_graphiti(settings: ZepEnvDep):
    client = ZepGraphiti()
    if settings.openai_base_url is not None:
        client.llm_client.config.base_url = settings.openai_base_url
    if settings.openai_api_key is not None:
        client.llm_client.config.api_key = settings.openai_api_key
    if settings.model_name is not None:
        client.llm_client.model = settings.model_name

    try:
        yield client
    finally:
        await client.close()


async def initialize_graphiti(settings: ZepEnvDep):
    global _global_graphiti_instance
    client = ZepGraphiti()
    await client.build_indices_and_constraints()
    _global_graphiti_instance = client


def get_graphiti_instance() -> Optional['ZepGraphiti']:
    """Get the global graphiti instance."""
    return _global_graphiti_instance


def get_fact_result_from_edge(edge: EntityEdge):
    return FactResult(
        uuid=edge.uuid,
        name=edge.name,
        fact=edge.fact,
        valid_at=edge.valid_at,
        invalid_at=edge.invalid_at,
        created_at=edge.created_at,
        expired_at=edge.expired_at,
    )


ZepGraphitiDep = Annotated[ZepGraphiti, Depends(get_graphiti)]
