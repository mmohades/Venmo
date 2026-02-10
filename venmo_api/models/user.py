from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel, EmailStr


class PaymentPrivacy(StrEnum):
    PRIVATE = auto()
    PUBLIC = auto()
    FRIENDS = auto()


class FriendStatus(StrEnum):
    FRIEND = auto()
    NOT_FRIEND = auto()


# TODO verify stuff that isn't personal
class IdentityType(StrEnum):
    PERSONAL = auto()
    BUSINESS = auto()
    CHARITY = auto()
    UNKNOWN = auto()

    @classmethod
    def _missing_(cls, value):  # type: ignore[override]
        """Gracefully handle new/unknown identity types coming from the API."""
        if isinstance(value, str):
            for member in cls:
                if member.value == value.lower():
                    return member
            return cls.UNKNOWN
        return None


class User(BaseModel):
    about: str
    date_joined: datetime
    friends_count: int | None
    is_active: bool
    is_blocked: bool
    friend_status: FriendStatus | None
    profile_picture_url: str
    username: str
    trust_request: str | None  # TODO, so far just None
    display_name: str
    email: EmailStr | None = None
    first_name: str
    id: str
    identity_type: IdentityType
    is_group: bool
    last_name: str
    phone: str | None = None
    is_payable: bool
    audience: PaymentPrivacy
