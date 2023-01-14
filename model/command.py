from dataclasses import dataclass, field
from itertools import chain

"""
Nested dataclass to use with ToyInfra.commands Queued Class
"""

@dataclass
class Command:
    _id: str = None
    action: str = None
    domain: str = None

    @classmethod
    def impl_list(cls):
        return {q.action: q for q in cls.__subclasses__()}

    @classmethod
    def __new__(cls, *args, **kwargs):
        t = cls.impl_list().get(kwargs.get('action')) or cls
        return object.__new__(t)

    @classmethod
    def all_fields(cls):
        fields = {
            str: 'text',
            int: 'number',
            float: 'number'
        }
        return {q: fields.get(z, 'text') for q, z in list(set((f, t) for f, t in chain(cls.__annotations__.items(), *[q.__annotations__.items() for q in cls.__subclasses__()])))}

@dataclass
class SyncCommand(Command):
    action: str = 'sync'
    folder: str = None
    file: str = None
    file_id: str = None

if __name__ == '__main__':
    print(Command.all_fields())