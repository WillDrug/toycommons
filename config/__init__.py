from time import time


class Config:
    DEFAULTS = {
        're_cache': 30,
        'base_url': 'http://localhost',
        'discovery_ttl': 5,
        'discovery_url': 'http://toydiscover',
        'drive_config_sync_ttl': 3000,
        'config_file_id': None,
        'drive_token': None,
        'drive_folder_id': None,
    }

    def __init__(self, collection):
        # database is used only to update. when sync becomes necessary, update this to insert
        # todo: recache timer.
        self.__collection = collection
        self.__recache()
        self.__updated = time()

    def __recache(self):
        for document in self.__collection.find():
            self.__setattr__(f'_{document["name"]}', document["value"])
        for param in self.DEFAULTS:
            if not hasattr(self, param):
                self.set_any(param, self.DEFAULTS[param])

    def set_any(self, key, value):
        self.__collection.update_one({'name': key}, {'$set': {'value': value}}, upsert=True)
        self.__setattr__(f'_{key}', value)

    @property
    def base_url(self):
        return self._base_url

    @property
    def recache(self):
        return self._re_cache

    @property
    def discovery_ttl(self):
        return self._discovery_ttl

    @property
    def discovery_url(self):
        return self._discovery_url

    @property
    def drive_token(self):
        return self._drive_token

    @drive_token.setter
    def drive_token(self, value: dict):
        self._drive_token = value
        self.__collection.update_one({'name': 'drive_token'}, {'$set': {'value': value}}, upsert=True)

    @property
    def drive_config_sync_ttl(self):
        return self._drive_config_sync_ttl

    @property
    def config_file_id(self):
        return self._config_file_id

    @property
    def drive_folder_id(self):
        return self._drive_folder_id
