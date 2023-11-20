from typing import List
from pydantic import BaseModel

class Vote(BaseModel):
    
    user_id : int
    positive : bool
