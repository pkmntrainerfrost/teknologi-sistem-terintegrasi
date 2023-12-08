from typing import Optional, List, Annotated
from enum import Enum
from beanie import Document, PydanticObjectId, Link, Indexed
from pydantic import Field, BaseModel
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase


class User(BeanieBaseUser, Document):

    username : Indexed(str, unique=True)
    displayname: Optional[str]
    bio: Optional[str]

class SlotStatus(str, Enum):

    open = "OPEN"
    taken = "TAKEN"
    closed = "CLOSED"

class WorkType(str, Enum):

    digital = "DIGITAL"
    furniture = "FURNITURE"

class CommissionSlot(Document):
    
    user : Indexed(str)
    slot_number : int
    status : SlotStatus
    worktype : WorkType
    title : str
    title_preprocessed : List[str]
    desc_general : Optional[str]
    desc_general_preprocessed : Optional[List[str]]
    desc_do : Optional[str]
    desc_dont : Optional[str]
    community_tags : bool
    tags : Optional[list[str]]
    price_lowerbound : int
    price_upperbound : int
    commissions_taken : int = 0
    rating : int = 0

    class Settings:
        name = "commissionslot"

class Tag(Document):

    title : str
    description : Optional[str]


    
async def get_user_db():

    yield BeanieUserDatabase(User)

class CommissionStatus(str, Enum):

    waiting = "WAITING"
    taken = "TAKEN"
    finished = "FINISHED"
    rejected = "REJECTED"

class Commission(Document):

    commissionslot: Indexed(str)
    commissioner: Indexed(str)
    commissionee: Indexed(str)
    description: str
    description_preprocessed: List[str]
    feedback: Optional[str]
    status: CommissionStatus
    rating_overall: Optional[float]
    rating_quality: Optional[int]
    rating_match: Optional[int] 
    rating_timeliness: Optional[int]
    furniture: Optional[int]

    class Settings:
        name = "commission"

class Df(Document):

    token: Indexed(str, unique = True)
    slots: List[str]

    class Settings:
        name = "df"
    
class TfIdf(Document):

    token: Indexed(str)
    slot: Indexed(str)
    value: float

    class Settings:
        name = "tfidf"