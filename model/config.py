from dataclasses import dataclass

@dataclass
class ConfigData:
    _id: str = None
    name: str = "config"
    base_url: str = 'http://127.0.0.1'
    discovery_ttl: int = 5
    re_cache: int = 30
    discovery_url: str = 'http://toydiscover'
    config_sync_ttl: int = 30
    config_file_id: str = None
    drive_token: dict = None
    drive_folder_id: str = None
    drive_config_sync_ttl: int = 3000