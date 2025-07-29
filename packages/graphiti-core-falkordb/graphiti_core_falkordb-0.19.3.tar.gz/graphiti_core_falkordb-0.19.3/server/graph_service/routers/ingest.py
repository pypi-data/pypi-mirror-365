import asyncio
import logging
from contextlib import asynccontextmanager
from functools import partial
from datetime import datetime

from fastapi import APIRouter, FastAPI, HTTPException, Query, status
from graphiti_core_falkordb.nodes import EpisodeType  # type: ignore
from graphiti_core_falkordb.utils.maintenance.graph_data_operations import clear_data  # type: ignore

from graph_service.dto import AddEntityNodeRequest, AddMessagesRequest, AddMessagesWithEntityTypesRequest, Message, Result
from graph_service.zep_graphiti import ZepGraphitiDep
from graph_service.entity_type_manager import entity_type_manager

logger = logging.getLogger(__name__)


class AsyncWorker:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.task = None
        self.processed_count = 0
        self.error_count = 0

    async def worker(self):
        logger.info("AsyncWorker started")
        while True:
            try:
                queue_size = self.queue.qsize()
                logger.info(f'Got a job: (size of remaining queue: {queue_size})')
                job = await self.queue.get()

                start_time = datetime.now()
                try:
                    await job()
                    self.processed_count += 1
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.info(f'Job completed successfully in {duration:.2f}s (total processed: {self.processed_count})')
                except Exception as e:
                    self.error_count += 1
                    duration = (datetime.now() - start_time).total_seconds()
                    logger.error(f'Job failed after {duration:.2f}s (total errors: {self.error_count}): {str(e)}', exc_info=True)
                finally:
                    self.queue.task_done()

            except asyncio.CancelledError:
                logger.info("AsyncWorker cancelled")
                break
            except Exception as e:
                logger.error(f'Unexpected error in AsyncWorker: {str(e)}', exc_info=True)

    async def start(self):
        logger.info("Starting AsyncWorker")
        self.task = asyncio.create_task(self.worker())

    async def stop(self):
        logger.info("Stopping AsyncWorker")
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

        # Clear remaining jobs
        remaining_jobs = 0
        while not self.queue.empty():
            self.queue.get_nowait()
            remaining_jobs += 1

        if remaining_jobs > 0:
            logger.warning(f"Cleared {remaining_jobs} unprocessed jobs from queue")

        logger.info(f"AsyncWorker stopped. Stats: {self.processed_count} processed, {self.error_count} errors")


async_worker = AsyncWorker()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await async_worker.start()
    yield
    await async_worker.stop()


router = APIRouter(lifespan=lifespan)


@router.post('/messages', status_code=status.HTTP_202_ACCEPTED)
async def add_messages(
    request: AddMessagesRequest,
    graphiti: ZepGraphitiDep,
    entity_type_names: str = Query(None, description="Comma-separated list of entity type names to use. If not provided, all registered entity types will be used automatically."),
    excluded_entity_types: str = Query(None, description="Comma-separated list of entity type names to exclude"),
    auto_discover_entities: bool = Query(True, description="Whether to automatically discover and register new entity types from the message content"),
):
    print(f"DEBUG: add_messages called with auto_discover_entities={auto_discover_entities}")
    logger.info(f"add_messages called with auto_discover_entities={auto_discover_entities}")
    # Auto-discover new entity types if enabled
    # NOTE: Auto-discovery is now highly restrictive and only creates core business entity types
    # suitable for CRM/KMS/IMS systems (Customer, Project, Task, Company, Contact, etc.)
    if auto_discover_entities and request.messages:
        print(f"DEBUG: Starting auto-discovery for {len(request.messages)} messages")
        # Combine all message content for analysis
        combined_content = " ".join([msg.content for msg in request.messages])
        print(f"DEBUG: Combined content: {combined_content}")
        logger.info(f"Attempting auto-discovery for content: {combined_content}")
        try:
            print("DEBUG: Calling entity_type_manager.discover_and_register_from_message")
            discovered_types = await entity_type_manager.discover_and_register_from_message(combined_content)
            print(f"DEBUG: Auto-discovery returned: {discovered_types}")
            if discovered_types:
                logger.info(f"Auto-discovered and registered entity types: {discovered_types}")
            else:
                logger.info("No entity types were auto-discovered (restrictive filtering applied)")
        except Exception as e:
            print(f"DEBUG: Auto-discovery exception: {e}")
            logger.error(f"Auto-discovery failed: {e}")

    # Parse entity type parameters
    entity_types = None
    if entity_type_names:
        type_names = [name.strip() for name in entity_type_names.split(',')]
        entity_types = await entity_type_manager.get_pydantic_models(type_names)
        if len(entity_types) != len(type_names):
            missing_types = set(type_names) - set(entity_types.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown entity types: {list(missing_types)}"
            )
    else:
        # Auto-detect: use all registered entity types if none specified
        entity_types = await entity_type_manager.get_pydantic_models()
        print(f"DEBUG: Available entity types after auto-discovery: {list(entity_types.keys()) if entity_types else 'None'}")
        if entity_types:
            logger.info(f"Auto-detected entity types: {list(entity_types.keys())}")

    # Handle excluded entity types by filtering from entity_types
    if excluded_entity_types and entity_types:
        excluded_types = [name.strip() for name in excluded_entity_types.split(',')]
        entity_types = {k: v for k, v in entity_types.items() if k not in excluded_types}
        logger.info(f"Excluded entity types: {excluded_types}")

    async def add_messages_task(m: Message):
        try:
            logger.info(f"Processing message: {m.name} for group {request.group_id}")

            # Enhanced source description with URL and metadata
            enhanced_source_description = m.source_description
            if m.source_url:
                enhanced_source_description += f" | Source URL: {m.source_url}"
            if m.source_metadata:
                metadata_str = ", ".join([f"{k}: {v}" for k, v in m.source_metadata.items()])
                enhanced_source_description += f" | Metadata: {metadata_str}"

            await graphiti.add_episode(
                uuid=m.uuid,
                group_id=request.group_id,
                name=m.name,
                episode_body=f'{m.role or ""}({m.role_type}): {m.content}',
                reference_time=m.timestamp,
                source=EpisodeType.message,
                source_description=enhanced_source_description,
                entity_types=entity_types,
            )
            logger.info(f"Successfully processed message: {m.name}")
        except Exception as e:
            logger.error(f"Failed to process message {m.name}: {str(e)}", exc_info=True)
            raise

    for m in request.messages:
        await async_worker.queue.put(partial(add_messages_task, m))

    return Result(message='Messages added to processing queue', success=True)


@router.post('/messages-with-entity-types', status_code=status.HTTP_202_ACCEPTED)
async def add_messages_with_entity_types(
    request: AddMessagesWithEntityTypesRequest,
    graphiti: ZepGraphitiDep,
):
    """
    Add messages to the graph with custom entity types.

    This endpoint allows you to specify which custom entity types to use
    when processing the messages, enabling more precise entity extraction.

    If entity_type_names is not provided or is empty, all registered entity
    types will be used automatically for entity extraction.
    """
    # Auto-discover new entity types if enabled
    if request.auto_discover_entities and request.messages:
        # Combine all message content for analysis
        combined_content = " ".join([msg.content for msg in request.messages])
        discovered_types = await entity_type_manager.discover_and_register_from_message(combined_content)
        if discovered_types:
            logger.info(f"Auto-discovered and registered entity types: {discovered_types}")

    # Get the entity type models
    entity_types = None
    if request.entity_type_names:
        entity_types = await entity_type_manager.get_pydantic_models(request.entity_type_names)
        if len(entity_types) != len(request.entity_type_names):
            missing_types = set(request.entity_type_names) - set(entity_types.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown entity types: {list(missing_types)}"
            )
    else:
        # Auto-detect: use all registered entity types if none specified
        entity_types = await entity_type_manager.get_pydantic_models()
        if entity_types:
            logger.info(f"Auto-detected entity types: {list(entity_types.keys())}")

    # Handle excluded entity types by filtering from entity_types
    if request.excluded_entity_types and entity_types:
        entity_types = {k: v for k, v in entity_types.items() if k not in request.excluded_entity_types}
        logger.info(f"Excluded entity types: {request.excluded_entity_types}")

    async def add_messages_task(m: Message):
        try:
            logger.info(f"Processing message with entity types: {m.name} for group {request.group_id}")
            logger.debug(f"Entity types: {list(entity_types.keys()) if entity_types else 'None'}")

            # Enhanced source description with URL and metadata
            enhanced_source_description = m.source_description
            if m.source_url:
                enhanced_source_description += f" | Source URL: {m.source_url}"
            if m.source_metadata:
                metadata_str = ", ".join([f"{k}: {v}" for k, v in m.source_metadata.items()])
                enhanced_source_description += f" | Metadata: {metadata_str}"

            await graphiti.add_episode(
                uuid=m.uuid,
                group_id=request.group_id,
                name=m.name,
                episode_body=f'{m.role or ""}({m.role_type}): {m.content}',
                reference_time=m.timestamp,
                source=EpisodeType.message,
                source_description=enhanced_source_description,
                entity_types=entity_types,
            )
            logger.info(f"Successfully processed message with entity types: {m.name}")
        except Exception as e:
            logger.error(f"Failed to process message with entity types {m.name}: {str(e)}", exc_info=True)
            raise

    for m in request.messages:
        await async_worker.queue.put(partial(add_messages_task, m))

    return Result(message='Messages with entity types added to processing queue', success=True)


@router.post('/entity-node', status_code=status.HTTP_201_CREATED)
async def add_entity_node(
    request: AddEntityNodeRequest,
    graphiti: ZepGraphitiDep,
):
    node = await graphiti.save_entity_node(
        uuid=request.uuid,
        group_id=request.group_id,
        name=request.name,
        summary=request.summary,
    )
    return node


@router.delete('/entity-edge/{uuid}', status_code=status.HTTP_200_OK)
async def delete_entity_edge(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_entity_edge(uuid)
    return Result(message='Entity Edge deleted', success=True)


@router.delete('/group/{group_id}', status_code=status.HTTP_200_OK)
async def delete_group(group_id: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_group(group_id)
    return Result(message='Group deleted', success=True)


@router.delete('/episode/{uuid}', status_code=status.HTTP_200_OK)
async def delete_episode(uuid: str, graphiti: ZepGraphitiDep):
    await graphiti.delete_episodic_node(uuid)
    return Result(message='Episode deleted', success=True)


@router.post('/clear', status_code=status.HTTP_200_OK)
async def clear(
    graphiti: ZepGraphitiDep,
):
    await clear_data(graphiti.driver)
    await graphiti.build_indices_and_constraints()
    return Result(message='Graph cleared', success=True)


@router.get('/worker-status', status_code=status.HTTP_200_OK)
async def get_worker_status():
    """Get the status of the background worker."""
    return {
        "worker_running": async_worker.task is not None and not async_worker.task.done(),
        "queue_size": async_worker.queue.qsize(),
        "processed_count": async_worker.processed_count,
        "error_count": async_worker.error_count,
        "success_rate": (
            async_worker.processed_count / (async_worker.processed_count + async_worker.error_count) * 100
            if (async_worker.processed_count + async_worker.error_count) > 0
            else 0
        )
    }


@router.post('/test-direct-episode', status_code=status.HTTP_201_CREATED)
async def test_direct_episode(graphiti: ZepGraphitiDep):
    """Test adding an episode directly (synchronously) to verify Graphiti is working."""
    try:
        logger.info("Testing direct episode addition")
        result = await graphiti.add_episode(
            name="Direct Test Episode",
            episode_body="This is a direct test episode to verify Graphiti functionality",
            source=EpisodeType.text,
            group_id="test_direct",
            reference_time=datetime.now(),
            source_description="Direct test"
        )
        logger.info("Direct episode added successfully")
        return {"message": "Direct episode added successfully", "success": True}
    except Exception as e:
        logger.error(f"Failed to add direct episode: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add episode: {str(e)}")
