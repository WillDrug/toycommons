from dataclasses import dataclass


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

@dataclass
class SyncCommand(Command):
    action: str = 'sync'
    folder: str = None
    file: str = None
    file_id: str = None



if __name__ == '__main__':
    def test():
        for q in range(10):
            a = yield q
            if a:
                print('gotcha')

    getter = test()
    for z in getter:
        if z == 9:
            getter.send(True)
