from dataclasses import asdict



class QueuedDataClass:
    datacls = None

    def __init__(self, collection, datacls=None):
        if datacls is not None:
            self.datacls = datacls
        self.__collection = collection

    def insert(self, obj):
        ins = asdict(obj)
        del ins['_id']
        self.__collection.insert_one(ins)

    def get_all(self, **query):
        return [self.datacls(**q) for q in self.__collection.find(query)]

    def get_queue(self, **query):
        """
        This will throw StopIteration which has to be handled
        :param query:
        :return:
        """
        for cmd in self.get_all(**query):
            accepted = yield cmd
            if accepted:
                self.delete_command(cmd)

    def delete(self, obj):
        self.__collection.commands.delete_one({"_id": obj._id})
