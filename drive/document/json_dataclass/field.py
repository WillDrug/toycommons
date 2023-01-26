class Field:
    def __init__(self, name, alt_names=(), strict=False, default=None):
        self.name = name
        self.alt_names = alt_names
        self.strict = strict
        self.default = default

    @staticmethod
    def get_data(name, data):
        for k in name.split('.'):
            if k not in data:
                return None
            data = data[k]
        return data

    @staticmethod
    def name_exists(name, data):
        for k in name.split('.'):
            if k not in data:
                return False
            data = data[k]
        return True

    def __call__(self, json_data):
        if self.name_exists(self.name, json_data):
            return self.get_data(self.name, json_data)

        for field in self.alt_names:
            if self.name_exists(field, json_data):
                return self.get_data(field, json_data)

        if self.default is not None:
            return self.default

        if self.strict:
            raise AttributeError(f'Did not find any of the expected names: {self.name}, {self.alt_names}')
        else:
            return None


class PackField(Field):
    def __init__(self, alt_names, strict=False, default=None):
        super().__init__(None, alt_names=alt_names, strict=strict, default=default)

    def __call__(self, json_data):
        return {
            k: self.get_data(k, json_data)
            for k in self.alt_names
        }
