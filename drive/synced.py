from time import time


class SyncedFile:
    def __init__(self, config, domain, name, request_function, process_function=lambda data: data.decode(),
                 filename=None, sync_time=None):
        self.__config = config
        self.domain = domain
        self.name = name
        self.filename = filename
        self.__sync_time = sync_time
        self.__cached = 0
        self.__request = request_function
        self.__process = process_function
        self.__data = None
        if self.filename is not None:
            try:
                with open(self.filename, 'r') as f:
                    self.__data = f.read()
            except FileNotFoundError as e:
                pass
        if self.__data is None:
            self.sync()

    def sync(self):
        self.__data = self.__process(self.__request())
        if self.filename is not None:
            with open(self.filename, 'wb') as f:
                f.write(self.__data)

    @property
    def data(self):
        if self.__sync_time is not None and self.__cached - time() < -self.__sync_time:
            self.sync()
        cmds = self.__config.get_commands(domain=self.domain, name=self.name, action='sync')
        if cmds.__len__() > 0:
            self.sync()
            for c in cmds:
                self.__config.delete_command(c)
        return self.__data