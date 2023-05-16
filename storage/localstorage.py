from typing import Any

from .metastorage import AbstractCollection, AbstractDatabase, AbstractStorage


class LocalCollection(AbstractCollection):
    def __process_update(self, obj, update):
        def set_field(obj, set_update):
            if not isinstance(set_update, dict):
                return set_update
            for k in set_update:  # {'field1': 'value', 'field2': {}}
                if k in obj and isinstance(obj[k], dict) and isinstance(set_update[k], dict):
                    obj[k] = set_field(obj[k], set_update[k])  # go field by field
                else:
                    obj[k] = set_update[k]
            return obj

        if any(q not in ('$set', '$unset', '$replaceRoot', '$replaceWith') for q in update.keys()):
            raise NotImplementedError(f'Implement instructions for localstorage, keys are: {update.keys()}')

        if '$replaceRoot' in update.keys() or '$replaceWith' in update.keys():
            obj = update.get('$replaceRoot') or update.get('$replaceWith')
            return obj
        if '$set' in update:
            for k in update['$set']:
                obj[k] = set_field(obj.get(k), update['$set'][k])

        if '$unset' in update:
            for field in update['$unset']:
                if field in obj:
                    del obj[field]

        return obj

    def update_one(self, u_filter, data, upsert=False):
        for i, o in enumerate(self.__data):
            if self.__process_filter(o, u_filter):
                self.__data[i] = self.__process_update(o, data)
                break
        else:
            if upsert:
                return self.insert_one(self.__process_update({}, data))

    def update_many(self, u_filter, data, upsert=False):
        updated = False
        for i, o in enumerate(self.__data):
            if self.__process_filter(o, u_filter):
                self.__data[i] = self.__process_update(o, data)
                updated = True
        if not updated and upsert:
            return self.insert_one(self.__process_update({}, data))

    def __init__(self, name, *args, **kwargs):
        self.__name = name
        self.__data = []

    def insert_one(self, data: dict) -> bool:
        self.__data.append(data)

    def insert_many(self, data: dict) -> bool:
        self.__data.extend(data)
        return True

    def __process_filter(self, data, rules):
        if rules is None:
            return True
        if data is None:
            return False
        for k in rules:
            if k.startswith('$'):
                if k == '$or':
                    result = any(self.__process_filter(data, q) for q in rules[k])
                elif k == '$and':
                    result = all(self.__process_filter(data, q) for q in rules[k])
                elif k == '$nor':
                    result = not any(self.__process_filter(data, q) for q in rules[k])
                else:
                    raise NotImplementedError(f'Please generate {k} filter for LocalStorage')
                if not result:
                    return False
                continue
            # it's a field
            if k not in data:
                return False
            key_data = data[k]
            if isinstance(key_data, dict):  # nested rule
                result = self.__process_filter(key_data, rules[k])
            else:
                result = key_data == rules[k]
            if not result:
                return False
        return True

    def find(self, filter_rules: dict = None) -> list:
        return [q for q in self.__data if self.__process_filter(q, filter_rules)]

    def find_one(self, filter_rules: dict = None) -> Any:
        data = self.find(filter_rules)
        if data.__len__() == 0:
            return None
        return data.pop()

    def delete_one(self, filter_rules: dict) -> bool:
        for i, q in enumerate(self.__data):
            if self.__process_filter(q, filter_rules):
                break
        else:
            return False
        self.__data.pop(i)
        return True

    def delete_many(self, filter_rules: dict) -> bool:  # fixme return int?
        data = self.find(filter_rules)
        for o in data:
            self.__data.remove(o)
        return True

    def __getattr__(self, item):
        return self.__class__(item)


class LocalDatabase(AbstractDatabase):
    def __init__(self, name, *args, **kwargs):
        self.__name = name
        self.__cache = {}

    def __getattr__(self, item) -> AbstractCollection:
        if item not in self.__cache:
            self.__cache[item] = LocalCollection(item)
        return self.__cache[item]


class LocalStorage(AbstractStorage):
    def __init__(self, **kwargs):
        self.__cache = {}

    def __getattr__(self, item) -> AbstractDatabase:
        if item not in self.__cache:
            self.__cache[item] = LocalDatabase(item)
        return self.__cache[item]

