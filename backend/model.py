from pydantic import BaseModel
from typing import List
from datetime import datetime 

class PlaybookVersion(BaseModel):
    version :str
    content:str
    created_at: datetime

class Playbook(BaseModel):
    playbook_id:str
    latest_version:str
    version:List[PlaybookVersion]