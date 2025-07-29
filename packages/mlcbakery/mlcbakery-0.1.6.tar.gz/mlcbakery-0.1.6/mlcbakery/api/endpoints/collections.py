import fastapi
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload  # For eager loading entities
from sqlalchemy import func # Added for func.lower
from typing import List

from mlcbakery.models import Collection, Dataset, Agent
from mlcbakery.schemas.collection import (
    CollectionCreate,
    CollectionResponse,
    CollectionStorageResponse,
    CollectionEnvironmentResponse,
)
from mlcbakery.schemas.dataset import DatasetResponse
from mlcbakery.schemas.agent import AgentResponse
from mlcbakery.database import get_async_db  # Use async dependency
from mlcbakery.api.dependencies import verify_auth, verify_auth_with_write_access, apply_auth_to_stmt
from mlcbakery.api.access_level import AccessType, AccessLevel

router = fastapi.APIRouter()

@router.post("/collections/", response_model=CollectionResponse)
async def create_collection(
    collection: CollectionCreate,
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth_with_write_access)
):
    """
    Create a new collection (async).
    Admins can specify any owner_identifier, while regular users can only create collections for themselves.
    """

    # check if the collection already exists (case-insensitive)
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection.name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    existing_collection = result_coll.scalar_one_or_none()
    if existing_collection:
        raise fastapi.HTTPException(status_code=400, detail="Collection already exists")

    # Determine owner_identifier based on admin status
    if auth.get("access_type") == AccessType.ADMIN:
        # System admins can specify any owner_identifier or use their own if not provided
        owner_identifier = collection.owner_identifier or auth.get("identifier", "unknown")
    else:
        # All other users (including org admins) can only create collections for themselves
        # Ignore any provided owner_identifier and use their auth identifier
        owner_identifier = auth.get("identifier", "unknown")

    db_collection = Collection(
        name=collection.name,
        description=collection.description,
        storage_info=collection.storage_info,
        storage_provider=collection.storage_provider,
        environment_variables=collection.environment_variables,
        owner_identifier=owner_identifier
    )

    db.add(db_collection)
    await db.commit()
    await db.refresh(db_collection)
    
    # Create a default agent for the collection
    default_agent = Agent(
        name=f"{collection.name} Owner",
        type="owner",
        collection_id=db_collection.id  # Associate the agent with this collection
    )
    db.add(default_agent)
    await db.commit()
    await db.refresh(default_agent)
    
    return db_collection


@router.get("/collections/{collection_name}", response_model=CollectionResponse)
async def get_collection(
    collection_name: str, 
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth)
):
    """Get a collection by name (async)."""
    # Use case-insensitive matching to be consistent with creation
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()
    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.get("/list-collections/", response_model=List[CollectionResponse])
async def list_collections(
    skip: int = 0, limit: int = 100, db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth),
):
    """
    Get collections from the database with pagination (async).
    """
    if skip < 0 or limit < 0:
        raise fastapi.HTTPException(
            status_code=422, detail="Invalid pagination parameters"
        )
    
    stmt = select(Collection).offset(skip).limit(limit)
    stmt = apply_auth_to_stmt(stmt, auth)
    
    result = await db.execute(stmt)
    collections = result.scalars().all()
    return collections


@router.get(
    "/collections/{collection_name}/storage", response_model=CollectionStorageResponse
)
async def get_collection_storage_info(
    collection_name: str,
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth),
):
    """Get storage information for a specific collection.
    This endpoint requires authentication with collection access.
    """
    # First verify the collection exists
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    return collection


@router.patch(
    "/collections/{collection_name}/storage", response_model=CollectionStorageResponse
)
async def update_collection_storage_info(
    collection_name: str,
    storage_info: dict = fastapi.Body(...),
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth_with_write_access),
):
    """Update storage information for a specific collection.
    This endpoint requires write access to the collection.
    """
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    if "storage_info" in storage_info:
        collection.storage_info = storage_info["storage_info"]
    if "storage_provider" in storage_info:
        collection.storage_provider = storage_info["storage_provider"]

    await db.commit()
    await db.refresh(collection)

    return collection


@router.get(
    "/collections/{collection_name}/environment", response_model=CollectionEnvironmentResponse
)
async def get_collection_environment_variables(
    collection_name: str,
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth),
):
    """Get environment variables for a specific collection.
    This endpoint requires authentication with collection access.
    """
    # First verify the collection exists
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    return collection


@router.patch(
    "/collections/{collection_name}/environment", response_model=CollectionEnvironmentResponse
)
async def update_collection_environment_variables(
    collection_name: str,
    environment_data: dict = fastapi.Body(...),
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth_with_write_access),
):
    """Update environment variables for a specific collection.
    This endpoint requires write access to the collection.
    """
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    if "environment_variables" in environment_data:
        collection.environment_variables = environment_data["environment_variables"]

    await db.commit()
    await db.refresh(collection)

    return collection


@router.patch(
    "/collections/{collection_name}/owner", response_model=CollectionResponse
)
async def update_collection_owner(
    collection_name: str,
    owner_data: dict = fastapi.Body(...),
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth_with_write_access),
):
    """Update owner identifier for a specific collection.
    This endpoint requires write access to the collection.
    """
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    if "owner_identifier" in owner_data:
        collection.owner_identifier = owner_data["owner_identifier"]

    await db.commit()
    await db.refresh(collection)

    return collection


@router.get(
    "/collections/{collection_name}/datasets/", response_model=List[DatasetResponse]
)
async def list_datasets_by_collection(
    collection_name: str,
    skip: int = fastapi.Query(default=0, description="Number of records to skip"),
    limit: int = fastapi.Query(
        default=100, description="Maximum number of records to return"
    ),
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth)
):
    """Get a list of datasets for a specific collection with pagination (async)."""
    # First verify the collection exists and user has access
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    # Query datasets associated with the collection ID
    stmt_datasets = (
        select(Dataset)
        .where(Dataset.collection_id == collection.id)
        .where(Dataset.entity_type == "dataset")  # Explicitly filter for datasets
        .options(
            selectinload(Dataset.collection)
        )
        .offset(skip)
        .limit(limit)
        .order_by(Dataset.id)  # Add consistent ordering
    )
    result_datasets = await db.execute(stmt_datasets)
    datasets = result_datasets.scalars().unique().all()
    return datasets


@router.get(
    "/collections/{collection_name}/agents/", response_model=List[AgentResponse]
)
async def list_agents_by_collection(
    collection_name: str,
    skip: int = fastapi.Query(default=0, description="Number of records to skip"),
    limit: int = fastapi.Query(
        default=100, description="Maximum number of records to return"
    ),
    db: AsyncSession = fastapi.Depends(get_async_db),
    auth = fastapi.Depends(verify_auth)
):
    """Get a list of agents for a specific collection with pagination (async)."""
    # First verify the collection exists and user has access
    stmt_coll = select(Collection).where(func.lower(Collection.name) == func.lower(collection_name))
    stmt_coll = apply_auth_to_stmt(stmt_coll, auth)
    result_coll = await db.execute(stmt_coll)
    collection = result_coll.scalar_one_or_none()

    if not collection:
        raise fastapi.HTTPException(status_code=404, detail="Collection not found")

    # Query agents associated with the collection ID
    stmt_agents = (
        select(Agent)
        .where(Agent.collection_id == collection.id)
        .offset(skip)
        .limit(limit)
        .order_by(Agent.id)  # Add consistent ordering
    )
    result_agents = await db.execute(stmt_agents)
    agents = result_agents.scalars().all()
    return agents
