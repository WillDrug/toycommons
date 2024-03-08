from dataclasses import asdict, fields


class MessageDataClass:
    """
    DataClass based MongoDB access which upserts "messages".
    Expects dataclass to hold recipient and domain fields to filter.
    Upserts instead of inserting by recipient+domain;
    Deletes on get immediately. guarantees delivery but not usage.
    """
    datacls = None

    def __init__(self, collection, datacls=None):
        """
        :param collection: MongoDB Collection
        :param datacls: Dataclass. This or cls.datacls should be set.
        """
        if datacls is not None:
            self.datacls = datacls
        # test Dataclass
        names = [q.name for q in fields(self.datacls)]
        if 'domain' not in names or 'recipient' not in names:
            raise AttributeError(f'MessageDataClass storage expects a dataclass with domain and recepient fields,'
                                 f'got {self.datacls}')
        self.__collection = collection

    def send(self, obj):
        """
        Insert object into inbox
        :param obj: Dataclass instance
        :return: None
        """
        ins = asdict(obj)
        del ins['_id']
        self.__collection.update_one({'domain': obj.domain, 'recipient': obj.recipient},
                                     {'$set': ins}, upsert=True)

    def receive(self, domain, recipient, message=None) -> dict | list:
        filter = {'domain': domain, 'recipient': recipient}
        if message is not None:
            filter['message'] = message
        if message is not None:
            data = self.__collection.find_one(filter)
            if data is not None:
                self.__collection.delete_one({'domain': domain, 'recipient': recipient})
        else:  # todo test this up, I'm not sure this works liek I want it to; but it won't be used yet.
            data = self.__collection.find_many(filter)
            if data is not None:
                self.__collection.delete_many(data)

        return data
