from pydantic import BaseModel

"""
Dataclass for toydiscovery mechanism
"""

class Service(BaseModel):
    host: str
    name: str
    description: str
    tags: list = None
    image: str = None
