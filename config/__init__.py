from time import time
from functools import wraps
from toycommons.model.command import Command
from dataclasses import asdict
from dataclasses import dataclass, asdict, fields


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

class Config:
    def __init__(self, collection):
        self._last_cached = time()
        self.__collection = collection
        self.config = None
        self.load()

    def load(self):
        data = {q['name']: q['value'] for q in self.__collection.config.find()}
        self.config = ConfigData(**data)

    def save(self, key, value):
        self.__collection.config.update_one({'name': key}, {'$set': {'value': value}})

    def __getattr__(self, item):
        if item in [q.name for q in fields(ConfigData)]:
            if time()-self._last_cached > self.config.re_cache:
                self.load()
                self._last_cached = time()
            return getattr(self.config, item)
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in [q.name for q in fields(ConfigData)]:
            try:
                return setattr(self.config, key, value)
            finally:
                self.save(key, value)
        return super().__setattr__(key, value)

    def __setitem__(self, key, value):
        if key not in [q.name for q in fields(ConfigData)]:
            raise AttributeError(f'{key} is not a valid config entry')
        try:
            return setattr(self.config, key, value)
        finally:
            self.save(key, value)

    def __getitem__(self, item):
        if item not in [q.name for q in fields(ConfigData)]:
            raise AttributeError(f'{item} is not a valid config entry')
        if time()-self._last_cached > self.config.re_cache:
            self.load()
            self._last_cached = time()
        return getattr(self.config, item)

    def add_command(self, command):
        self.__collection.commands.insert_one(asdict(command))

    def get_commands(self, **query):
        return [Command(**q) for q in self.__collection.commands.find(query)]

    def get_commands_queue(self, **query):
        for cmd in self.get_commands(**query):
            accepted = yield cmd
            if accepted:
                self.delete_command(cmd)

    def delete_command(self, command):
        self.__collection.commands.delete_one({"_id": command._id})