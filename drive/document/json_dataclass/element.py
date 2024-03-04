from .field import Field
from types import FunctionType
import json


class Element:
    def __init__(self, json_data):
        if isinstance(json_data, str):
            json_data = json.loads(json_data)
        self._json_data = json_data
        for attr, attr_data in self._attributes.items():
            if isinstance(attr_data['json_name'], str):
                data = Field.get_data(attr_data['json_name'], json_data)
            else:  # Field class
                data = attr_data['json_name'](json_data)
            setattr(self, attr, self._process(attr, attr_data['datatype'], data))

    @property
    def _attributes(self):
        return {
            attr:
                {
                    'json_name': cls.__dict__.get(attr),
                    'datatype': cls.__dict__.get('__annotations__', {}).get(attr, str)
                }
            for cls in self.__class__.mro() for attr in cls.__dict__.keys()
            if not attr.startswith('_') and not isinstance(cls.__dict__[attr], FunctionType)
               and not isinstance(cls.__dict__[attr], property)
        }

    def _process(self, attr, datatype, value):
        if hasattr(self, f'_{attr}'):
            return getattr(self, f'_{attr}')(value)
        if value is None:
            return None
        return datatype(value)

    def __str__(self):
        return f'<{self.__class__.__name__}: ({", ".join([q for q in self._attributes])})>'

    def __repr__(self):
        return self.__str__()


class BackReference:
    def __init__(self, class_ref: str):
        self.class_ref = class_ref

    def __call__(self, json_data):
        return self.get_class()(json_data)

    def get_class(self):
        return {q.__name__: q for q in Element.__subclasses__()}[self.class_ref]

    def __name__(self):
        return self.class_ref

    def get_type(self):
        def new_new(cls, *args, **kwargs):
            return self.get_class()(*args, **kwargs)

        return type(f'BackReferenceTo{self.class_ref}', (object,), {'__new__': new_new})


class AnyOfElement:
    def __new__(cls, cls_to_use):
        if isinstance(cls_to_use, BackReference):
            cls_to_use = cls_to_use.get_type()
        return type(f"{cls.__name__}{cls_to_use.__name__}", (cls_to_use,), {'__new__': cls.new_new})

    @staticmethod
    def new_new(cls, elem):
        return cls(elem)


class DictOfElement(AnyOfElement):
    @staticmethod
    def new_new(cls, elem):
        ret = {}
        for k in elem:
            ret[k] = cls.mro()[1](elem[k])
        return ret


class ListOfElement(AnyOfElement):
    @staticmethod
    def new_new(cls, elem):
        return [cls.mro()[1](q) for q in elem]
