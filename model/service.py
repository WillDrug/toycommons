from pydantic import BaseModel

"""
Dataclass for toydiscovery mechanism
"""
# fixme: this is the only pydantic model. either switch all to it or this to dataclass


class Service(BaseModel):
    host: str
    name: str
    description: str
    tags: list = None
    image: str = None
