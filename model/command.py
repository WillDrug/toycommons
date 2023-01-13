from dataclasses import dataclass
from typing import Optional

@dataclass
class SyncCommand:
    _id: Optional[str]
    action: str
    domain: Optional[str]  # where None is ALL
    folder: Optional[str]  # where None is default
    file: Optional[str]
    file_id: Optional[str]
