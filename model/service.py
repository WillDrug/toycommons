from pydantic import BaseModel


class Service(BaseModel):
    host: str
    name: str
    description: str
