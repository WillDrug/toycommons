from dataclasses import dataclass
from typing import Optional

@dataclass
class Command:
    _id: Optional[str]
    action: str
    domain: Optional[str]  # where None is ALL
    folder: Optional[str]  # where None is default
    file: Optional[str]
    file_id: Optional[str]

    @property
    def db_id(self):
        return self._id