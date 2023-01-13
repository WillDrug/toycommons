from time import time
from functools import wraps
from toycommons.model.command import SyncCommand
from dataclasses import asdict
from dataclasses import dataclass, asdict, fields


@dataclass
class ConfigData:
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

class Config:
    def __init__(self, collection):
        self._last_cached = time()
        self.__collection = collection
        self.config = None
        self.load()

    def load(self):
        data = self.__collection.find_one({"name": "config"}) or {}
        self.config = ConfigData(**data)
        self._commands = self.__collection.find_one({"name": "commands"})

    def save(self):
        self.__collection.update_one({"name": "config"}, {"$set": asdict(self.config)}, upsert=True)

    def __getattr__(self, item):
        if item in [q.name for q in fields(ConfigData)]:
            if time()-self._last_cached > self.config.re_cache:
                self.load()
                self._last_cached = time()
            return getattr(self.config, item)
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in [q.name for q in fields(ConfigData)]:
            self.save()
            return setattr(self.config, key, value)
        return super().__setattr__(key, value)

    def __setitem__(self, key, value):
        if key not in [q.name for q in fields(ConfigData)]:
            raise AttributeError(f'{key} is not a valid config entry')
        setattr(self.config, key, value)

    def __getitem__(self, item):
        if item not in [q.name for q in fields(ConfigData)]:
            raise AttributeError(f'{item} is not a valid config entry')
        return getattr(self.config, item)

    def save_commands(self):
        self.__collection.update_one({"name": "commands"}, {"$set": self._commands}, upsert=True)

    def add_command(self, action, command):
        if action not in self._commands:
            raise TypeError(f'Action is not recognized and hasn\'t been dataclass\'d')
        self._commands[action].append(command)
        self.save_commands()

    def find_command(self, action, **query):
        return [q for q in self._commands.get(action, ()) if all(q[k] == query[k] for k in query)]

    def delete_command(self, action, command):
        self._commands[action].remove(command)
        self.save_commands()