from dataclasses import dataclass
from typing import Optional

@dataclass
class SyncCommand:
    file: str
    domain: str = None
    folder: str = None
    file_id: str = None
