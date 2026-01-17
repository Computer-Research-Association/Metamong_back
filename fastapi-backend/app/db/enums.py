from enum import Enum


class RoomRole(Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VISITOR = "VISITOR"


class AuthProvider(Enum):
    GOOGLE = "GOOGLE"
    LOCAL = "LOCAL"
