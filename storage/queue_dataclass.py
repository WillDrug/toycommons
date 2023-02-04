from dataclasses import asdict


class QueuedDataClass:
    """
    DataClass based MongoDB access which expects deletion of an item accepted.
    All dataclass objects expect to hold _id property.
    """
    datacls = None

    def __init__(self, collection, datacls=None):
        """
        :param collection: MongoDB Collection
        :param datacls: Dataclass. This or cls.datacls should be set.
        """
        if datacls is not None:
            self.datacls = datacls
        self.__collection = collection

    def insert(self, obj):
        """
        Insert object into queue
        :param obj: Dataclass instance
        :return: None
        """
        ins = asdict(obj)
        del ins['_id']
        self.__collection.insert_one(ins)

    def get_all(self, **query):
        """
        Regular DB access
        :param query: MongoDB query
        :return:
        """
        return [self.datacls(**q) for q in self.__collection.find(query)]

    def get_queue(self, **query):
        """
        This will throw StopIteration which has to be handled
        :param query: MongoDB query
        :return: generator expecting .send(True\False)
        """
        for cmd in self.get_all(**query):
            accepted = yield cmd
            if accepted:
                self.delete(cmd)

    def delete(self, obj):
        """
        Generic delete method
        :param obj: Object to delete (expects "_id")
        :return:
        """
        self.__collection.delete_one({"_id": obj._id})
