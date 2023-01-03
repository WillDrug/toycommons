from time import time


class Config:
    __re_cache: int = 30
    __discovery_ttl: int = 5
    __discovery_url: str = 'http://toydiscover'

    def __init__(self, collection):
        # database is used only to update. when sync becomes necessary, update this to insert
        # todo: recache timer.
        self.__collection = collection
        self.__recache()
        self.__updated = time()

    def __recache(self):
        for document in self.__collection.find():
            self.__setattr__(f'__{document["name"]}', document["value"])

    @property
    def recache(self):
        return self.__re_cache

    @property
    def discovery_ttl(self):
        return self.__discovery_ttl

    @property
    def discovery_url(self):
        return self.__discovery_url