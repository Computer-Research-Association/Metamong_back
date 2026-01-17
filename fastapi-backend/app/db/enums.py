from enum import Enum


class RoomRole(Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VISITOR = "VISITOR"


class AuthProvider(Enum):
    GOOGLE = "GOOGLE"
    LOCAL = "LOCAL"


class RC(Enum):
    Torrey = "Torrey"
    JangGiRyeo = "JangGiRyeo"
    Kuyper = "Kuyper"
    SonYangWon = "SonYangWon"
    Philadelphos = "Philadelphos"
    Carmichael = "Carmichael"

