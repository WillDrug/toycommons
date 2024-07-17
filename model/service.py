from pydantic import BaseModel
from typing import Optional

"""
Dataclass for toydiscovery mechanism
"""
# fixme: this is the only pydantic model. either switch all to it or this to dataclass


class Service(BaseModel):
    host: str
    name: str
    description: str
    tags: Optional[list] = None
    image: Optional[str] = None
