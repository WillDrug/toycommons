from typing import Any


class DomainNameValue:
    """
    Name-Value non-cached database access by attributes.
    """
    def __init__(self, domain: str, collection: "Collection"):
        """
        :param domain: App within toychest to filter data with (forced filter)
        :param collection: MongoDB Collection to use.
        """
        # This is set via __setattr__ to allow overrides to work.
        object.__setattr__(self, '_DomainNameValue__domain', domain)
        object.__setattr__(self, '_DomainNameValue__collection', collection)

    def clear(self):
        self.__collection.delete_many({'domain': self.__domain})

    def _get(self, item: str) -> Any:
        """
        Default getter of any items.
        :param item: any str
        :return: Any
        """
        d = self.__collection.find_one({"domain": self.__domain, "name": item}) or {}
        return d.get('value')

    def _set(self, key: str, value: Any) -> None:
        """
        Default setter
        :param key: AnyStr
        :param value: Any built-in
        :return: None
        """
        return self.__collection.\
            update_one({"name": key, "domain": self.__domain},
                       {"$set": {"domain": self.__domain,
                                 "name": key, "value": value}},
                       upsert=True)

    # next section proxies attribute and item access into _get and _set.

    def __getattr__(self, item):
        return self._get(item)

    def __setattr__(self, key, value):
        return self._set(key, value)

    def __setitem__(self, key, value):
        return self._set(key, value)

    def __getitem__(self, item):
        return self._get(item)

