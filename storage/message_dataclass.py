from dataclasses import asdict, fields


class MessageDataClass:
    """
    DataClass based MongoDB access which upserts "messages".
    Expects dataclass to hold recipient and domain fields to filter.
    Upserts instead of inserting by recipient+domain;
    Deletes on get immediately. guarantees delivery but not usage.


    For some stupid reason I made this to have only one message floating at all times...
    Dunno. Might fix later.
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

    def receive(self, domain, recipient) -> dict | None:
        """
        If you want to give several commands to one recipient, give them one by one, lol
        :param domain: Domain.
        :param recipient: Target
        :return:
        """
        filter = {'domain': domain, 'recipient': recipient}

        data = self.__collection.find_one(filter)

        if data is not None:
            self.__collection.delete_one({'domain': domain, 'recipient': recipient})
        # todo: return data, ok() callable.
        return data
