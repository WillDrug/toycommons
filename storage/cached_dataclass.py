from time import time
from dataclasses import fields


class CachedDataclass:
    datacls = None

    def __init__(self, collection, dcls=None):
        if dcls is not None:
            self.datacls = dcls
        self._last_cached = time()
        self.__collection = collection
        self.data = None
        self.load()

    @property
    def re_cache(self):
        return 30

    def load(self):
        data = {q['name']: q['value'] for q in self.__collection.find()}
        self.data = self.datacls(**data)

    def save(self, key, value):
        self.__collection.update_one({'name': key}, {'$set': {'value': value}})

    def __getattr__(self, item):
        if item in [q.name for q in fields(self.datacls)]:
            if time() - self._last_cached > self.re_cache:
                self.load()
                self._last_cached = time()
            return getattr(self.data, item)
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in [q.name for q in fields(self.datacls)]:
            try:
                return setattr(self.data, key, value)
            finally:
                self.save(key, value)
        return super().__setattr__(key, value)

    def __setitem__(self, key, value):
        if key not in [q.name for q in fields(self.datacls)]:
            raise AttributeError(f'{key} is not a valid config entry')
        try:
            return setattr(self.data, key, value)
        finally:
            self.save(key, value)

    def __getitem__(self, item):
        if item not in [q.name for q in fields(self.datacls)]:
            raise AttributeError(f'{item} is not a valid config entry')
        if time() - self._last_cached > self.re_cache:
            self.load()
            self._last_cached = time()
        return getattr(self.data, item)
