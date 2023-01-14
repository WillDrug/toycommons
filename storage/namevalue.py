



class DomainNameValue:
    def __init__(self, domain, collection):
        self.domain = domain
        self.__collection = collection

    def _get(self, item):
        d = self.__collection.cache.find_one({"domain": self.domain, "key": item})
        if d is None:
            return None
        else:
            return d["value"]

    def _set(self, key, value):
        return self.__collection.update_one({"name": key, "domain": self.domain}, {"domain": self.domain,
                                                                                   "name": key,
                                                                                   "value": value}, upsert=True)
    def __getattr__(self, item):
        return self._get(item)

    def __setattr__(self, key, value):
        return self._set(key, value)

    def __setitem__(self, key, value):
        return self._set(key, value)

    def __getitem__(self, item):
        return self._get(item)
