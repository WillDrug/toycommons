from time import time
import pickle


class SyncedFile:
    def __init__(self, config, domain, name, request_function, process_function=lambda data: data.decode(),
                 filename=None, sync_time=None, fid=None):
        self.__config = config
        self.domain = domain
        self.name = name
        self.filename = filename
        self.fid = fid
        self.__sync_time = sync_time
        self.__cached = 0
        self.__request = request_function
        self.__process = process_function
        self.__data = None
        if self.filename is not None:
            try:
                with open(self.filename, 'r') as f:
                    self.__data = pickle.loads(f.read())
            except FileNotFoundError as e:
                pass
        if self.__data is None:
            self.sync()

    def sync(self):
        self.__data = self.__process(self.__request())
        if self.filename is not None:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.__data, f)

    @property
    def data(self):
        if self.__sync_time is not None and self.__cached - time() < -self.__sync_time:
            self.sync()
        cmds_queue = self.__config.get_commands_queue(action='sync', domain=self.domain,
                                                      **{'$or': [
                                                          {'file': self.name},
                                                          {'$and':
                                                              [
                                                                  {'file_id': self.fid},
                                                                  {'$not': {'file_id': None}}
                                                              ]
                                                          }
                                                      ]})
        for _ in cmds_queue:
            self.sync()
            try:
                cmds_queue.send(True)
            except StopIteration:
                pass
        return self.__data
