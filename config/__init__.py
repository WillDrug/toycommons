from time import time


class Config:
    DEFAULTS = {
        '_re_cache': 30,
        '_base_url': 'http://localhost:8080',
        '_discovery_ttl': 5,
        '_discovery_url': 'http://toydiscover',
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
        self.__collection.update_one({'name': key}, {'value': value})
        self.__setattr__(f'_{key}', value)

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
        self.__collection.update_one({'name': 'drive_token'}, {'value': value})
