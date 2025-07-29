from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any


class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None


class CollectionCreate(CollectionBase):
    storage_info: Optional[Dict[str, Any]] = None
    storage_provider: Optional[str] = "default"
    environment_variables: Optional[Dict[str, Any]] = None
    owner_identifier: Optional[str] = None

class CollectionResponse(CollectionBase):
    id: int
    auth_org_id: Optional[str] = None  # TODO(jon): deprecate this
    owner_identifier: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class CollectionStorageResponse(CollectionResponse):
    storage_info: Optional[Dict[str, Any]] = None
    storage_provider: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CollectionEnvironmentResponse(CollectionResponse):
    environment_variables: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
