from typing import Optional, List
from beanie import PydanticObjectId
from app.models.models import CommissionSlot, WorkType, User
from pydantic import BaseModel, Field
import uuid
from typing import Optional, List
from beanie import PydanticObjectId
from fastapi_users import schemas

class UserRead(schemas.BaseUser[PydanticObjectId]):

    username : str
    displayname: Optional[str] | None = None
    bio: Optional[str] | None = None

class UserCreate(schemas.BaseUserCreate):

    username : str
    displayname: Optional[str] | None = None
    bio: Optional[str] | None = None

class UserUpdate(schemas.BaseUserUpdate):
    
    username : Optional[str] | None = None
    displayname: Optional[str] | None = None
    bio: Optional[str] | None = None

class CommissionSlotCreate(BaseModel):
    
    worktype : WorkType
    title : str
    desc_general : Optional[str] | None = None
    desc_do : Optional[str] | None = None
    desc_dont : Optional[str] | None = None
    community_tags : bool
    tags : Optional[List[str]] | None = None
    price_lowerbound : int
    price_upperbound : int

class CommissionSlotUpdate(BaseModel):

    worktype : Optional[WorkType] | None = None
    title : Optional[str] | None = None
    desc_general : Optional[str] | None = None
    desc_do : Optional[str] | None = None
    desc_dont : Optional[str] | None = None
    community_tags : Optional[bool] | None = None
    tags : Optional[List[str]] | None = None
    price_lowerbound : Optional[int] | None = None
    price_upperbound : Optional[int] | None = None

class CommissionCreate(BaseModel):

    description: str
    
class CommissionFeedback(BaseModel):

    feedback: str
    rating_quality: int
    rating_match: int
    rating_timeliness: int