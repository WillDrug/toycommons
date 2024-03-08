from dataclasses import dataclass, fields
from itertools import chain
from typing import Literal

"""
Message base dataclass to extend for message_dataclass.py usage
"""

@dataclass
class Message:
    recipient: str  # recipient identification determined with code usage
    message: str
    domain: str = None  # optional domain separation (one message per domain+recipient
    _id: str = None  # mongo proxy

@dataclass
class Command(Message):  # ignore IDE error. When you override a definition it builds in the right order anyway
    """
    Config is synced on Domain=None, Recipient='config'
    Files are synced on Domain+Filename (important! domains have different caches, yup)
    """
    message: Literal['sync']  # Commands have a limited number of messages to send.

if __name__ == '__main__':
    print(Message('file.txt', 'sync'))
    print(Command('file.txt', 'sync'))