from time import time
from functools import wraps
from toycommons.model.command import Command
from dataclasses import asdict


def cached(func):
    @wraps(func)
    def test_cache(self, *args, **kwargs):
        if time() - self._cached < self._config_sync_ttl:
            self.recache()
            self._last_cached = time()
        return func(self, *args, **kwargs)
    return test_cache


class Config:
    DEFAULTS = {
        're_cache': 30,
        'base_url': 'http://localhost',
        'discovery_ttl': 5,
        'discovery_url': 'http://toydiscover',
        'config_sync_ttl': 30,
        'config_file_id': None,
        'drive_token': None,
        'drive_folder_id': None
    }

    def __init__(self, collection, commands):
        # database is used only to update. when sync becomes necessary, update this to insert

        self._last_cached = time()
        self.__collection = collection
        self.__commands = commands
        self.recache()

    def recache(self):
        for document in self.__collection.find():
            self.__setattr__(f'_{document["name"]}', document["value"])
        for param in self.DEFAULTS:
            if not hasattr(self, f'_param'):
                self.set_any(param, self.DEFAULTS[param])
        self._commands = list(self.__commands.find())

    def set_any(self, key, value):
        self.__collection.update_one({'name': key}, {'$set': {'value': value}}, upsert=True)
        self.__setattr__(f'_{key}', value)

    @property
    @cached
    def base_url(self):
        return self._base_url

    @property
    @cached
    def discovery_ttl(self):
        return self._discovery_ttl

    @property
    @cached
    def discovery_url(self):
        return self._discovery_url

    @property
    @cached
    def drive_token(self):
        return self._drive_token

    @drive_token.setter
    def drive_token(self, value: dict):
        self._drive_token = value
        self.__collection.update_one({'name': 'drive_token'}, {'$set': {'value': value}}, upsert=True)

    @property
    @cached
    def drive_config_sync_ttl(self):
        return self._drive_config_sync_ttl

    @property
    @cached
    def config_file_id(self):
        return self._config_file_id

    @property
    @cached
    def drive_folder_id(self):
        return self._drive_folder_id

    @property
    @cached
    def commands(self):
        return [Command(**q) for q in self._commands]

    def get_commands(self, **query):
        return [q for q in self.commands if all([q[k] == query[k] for k in query])]

    def send_command(self, command):
        self.__commands.insert_one(asdict(command))

    def delete_command(self, command):
        self.__commands.delete_one({'_id': command.db_id})
