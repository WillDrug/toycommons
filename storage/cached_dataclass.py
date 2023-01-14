from time import time
from dataclasses import fields


class CachedDataclass:
    """
    Mongodb collection manipulation class which proxies a dataclass attributes as colleciton-stored.
    Either cls.datacls or self.dcls must be set.
    """
    datacls = None

    def __init__(self, collection, dcls=None):
        """
        :param collection: MongoDB Collection
        :param dcls: Any dataclass
        """
        if dcls is not None:
            self.datacls = dcls
        self._last_cached = time()
        self.__collection = collection
        self.data = None
        self.load()

    @property
    def re_cache(self) -> int:
        """
        Property to override to determine re-cache timing. todo: allow static replace into config default at startup
        :return: int
        """
        return 30

    def load(self):
        """
        Injest full data from collection
        :return: None
        """
        data = {q['name']: q['value'] for q in self.__collection.find()}
        self.data = self.datacls(**data)

    def save(self, key, value):
        """
        Update one item
        :param key: Key of item (dataclass field name)
        :param value: Value of item
        :return: None
        """
        self.__collection.update_one({'name': key}, {'$set': {'value': value}})

    def __getattr__(self, item: str):
        """
        Proxies attribute access into dataclass-based mongodb-access
        :param item: Default usage or dataclass field
        :return: Any
        """
        if item in [q.name for q in fields(self.datacls)]:
            if time() - self._last_cached > self.re_cache:
                self.load()
                self._last_cached = time()
            return getattr(self.data, item)
        return super().__getattribute__(item)

    def __setattr__(self, key: str, value) -> None:
        """
        Proxies attribute access to set dataclass-based fields in mongodb
        :param key: str. dataclass field
        :param value: Any
        :return:
        """
        if key in [q.name for q in fields(self.datacls)]:
            try:
                return setattr(self.data, key, value)
            finally:
                self.save(key, value)
        return super().__setattr__(key, value)

    def __setitem__(self, key, value):
        """
        Same proxy method for bracket access.
        :param key: Dataclass field str
        :param value: Any
        :return: None
        """
        if key not in [q.name for q in fields(self.datacls)]:
            raise AttributeError(f'{key} is not a valid config entry')
        try:
            return setattr(self.data, key, value)
        finally:
            self.save(key, value)

    def __getitem__(self, item):
        """
        Same proxy method for bracket access.
        :param item: Dataclass field str
        :return: Any
        """
        if item not in [q.name for q in fields(self.datacls)]:
            raise AttributeError(f'{item} is not a valid config entry')
        if time() - self._last_cached > self.re_cache:
            self.load()
            self._last_cached = time()
        return getattr(self.data, item)
