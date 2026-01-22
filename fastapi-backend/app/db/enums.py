from enum import Enum


class RoomRoleType(Enum):
    OWNER = "OWNER"
    EDITOR = "EDITOR"
    VISITOR = "VISITOR"


class AuthProvider(Enum):
    GOOGLE = "GOOGLE"
    NAVER = "NAVER"
    KAKAO = "KAKAO"
    LOCAL = "LOCAL"


class RC(Enum):
    Torrey = "Torrey"
    JangGiRyeo = "JangGiRyeo"
    Kuyper = "Kuyper"
    SonYangWon = "SonYangWon"
    Philadelphos = "Philadelphos"
    Carmichael = "Carmichael"


class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    DELETED = "DELETED"
    NEW = "NEW"
    GUEST = "GUEST"


class RoomType(Enum):
    GENERAL = "GENERAL"
    CUSTOM = "CUSTOM"
    BUILDING = "BUILDING"


class OwnerType(Enum):
    USER = "USER"
    TEAM = "TEAM"
    SYSTEM = "SYSTEM"


class FriendStatus(Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    BLOCKED = "BLOCKED"


class MBTI(Enum):
    ISTJ = "ISTJ"
    ISFJ = "ISFJ"
    INFJ = "INFJ"
    INTJ = "INTJ"
    ISTP = "ISTP"
    ISFP = "ISFP"
    INFP = "INFP"
    INTP = "INTP"
    ESTP = "ESTP"
    ESFP = "ESFP"
    ENFP = "ENFP"
    ENTP = "ENTP"
    ESTJ = "ESTJ"
    ESFJ = "ESFJ"
    ENFJ = "ENFJ"
    ENTJ = "ENTJ"
