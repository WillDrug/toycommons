class DomainNameValue:
    def __init__(self, domain, collection):
        object.__setattr__(self, 'domain', domain)
        object.__setattr__(self, 'collection', collection)

    def _get(self, item):
        d = object.__getattribute__(self, 'collection').find_one({"domain": object.__getattribute__(self, 'domain'),
                                                                  "key": item}) or {}
        return d.get('value')

    def _set(self, key, value):
        return object.__getattribute__(self, 'collection').\
            update_one({"name": key, "domain": object.__getattribute__(self, 'domain')},
                       {"$set": {"domain": object.__getattribute__(self, 'domain'),
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
