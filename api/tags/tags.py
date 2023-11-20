from typing import List
from pydantic import BaseModel

from ..votes import votes

class AppliedTag(BaseModel):
	tag_name: str
	votes: List[votes.Vote]
	community: bool