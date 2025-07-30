from chat_object.message import Message
from chat_object.chat import Chat
from chat_object.consts import (
    Role,
    MessageType,
    DictMessageType,
    LiteralRoleType,
    RoleType,
)

__all__ = [
    "Message",
    "Chat",
    "Role",
    "MessageType",
    "DictMessageType",
    "LiteralRoleType",
    "RoleType",
]

__version__ = "1.0.0"
__author__ = "fresh-milkshake"
__license__ = "MIT"
__url__ = "https://github.com/fresh-milkshake/chat-object"
__description__ = "A simple library for creating and manipulating chat and message objects for LLM applications"