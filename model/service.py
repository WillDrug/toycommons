from pydantic import BaseModel


class Service(BaseModel):
    host: str
    name: str
    description: str
    tags: list = None
    image: str = None
