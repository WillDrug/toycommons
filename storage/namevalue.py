class DomainNameValue:
    def __init__(self, domain, collection):
        object.__setattr__(self, '_DomainNameValue__domain', domain)
        object.__setattr__(self, '_DomainNameValue__collection', collection)

    def _get(self, item):
        print(f'called item {item} get')
        d = self.__collection.find_one({"domain": self.__domain, "key": item}) or {}
        return d.get('value')

    def _set(self, key, value):
        print(f'Called set for {key} with {value}')
        return self.__collection.\
            update_one({"name": key, "domain": self.__domain},
                       {"$set": {"domain": self.__domain,
                                 "name": key, "value": value}},
                       upsert=True)

    def __getattr__(self, item):
        return self._get(item)

    def __setattr__(self, key, value):
        return self._set(key, value)

    def __setitem__(self, key, value):
        return self._set(key, value)

    def __getitem__(self, item):
        return self._get(item)

