from abc import ABCMeta, abstractmethod
from typing import Any
from typing import Iterable


class AbstractCollection:
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def insert_one(self, data: dict) -> bool:
        pass

    @abstractmethod
    def insert_many(self, data: Iterable) -> bool:
        pass

    @abstractmethod
    def update_one(self, filter, data, upsert=False):
        pass

    @abstractmethod
    def update_many(self, filter, data, upsert=False):
        pass

    @abstractmethod
    def find(self, filter_rules: dict = None) -> list:
        pass

    @abstractmethod
    def find_one(self, filter_rules: dict = None) -> dict:
        pass

    @abstractmethod
    def delete_one(self, filter_rules: dict) -> bool:
        pass

    @abstractmethod
    def delete_many(self, filter_rules: dict) -> bool:
        pass

    @abstractmethod
    def __getattr__(self, item):
        pass


class AbstractDatabase:
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def __getattr__(self, item) -> AbstractCollection:
        pass


class AbstractStorage(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def __getattr__(self, item) -> AbstractDatabase:
        pass
