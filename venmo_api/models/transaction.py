from datetime import datetime
from enum import Enum
from typing import Annotated, Literal

from pydantic import AliasPath, BaseModel, BeforeValidator, Field

from venmo_api.models.payment import Payment
from venmo_api.models.user import PaymentPrivacy, User

DEVICE_MAP = {1: "iPhone", 4: "Android", 10: "Desktop Browser", 0: "Other"}


def get_device_model_from_json(app_json: dict):
    """
    extract the phone model from app_info json.
    :param app_json:
    :return:
    """
    _id = 0
    if app_json:
        _id = app_json["id"]

    return DEVICE_MAP.get(int(_id))


DeviceModel = Annotated[
    Literal["iPhone", "Android", "Other"], BeforeValidator(get_device_model_from_json)
]


class TransactionType(Enum):
    PAYMENT = "payment"
    # merchant refund
    REFUND = "refund"
    # to/from bank account
    TRANSFER = "transfer"
    # add money to debit cards
    TOP_UP = "top_up"
    # debit card purchase
    AUTHORIZATION = "authorization"
    # debit card atm withdrawal
    ATM_WITHDRAWAL = "atm_withdrawal"

    DISBURSEMENT = "disbursement"


class Mention(BaseModel):
    username: str
    user: User


class Comment(BaseModel):
    id: str
    message: str
    date_created: datetime
    mentions: list[Mention] = Field(validation_alias=AliasPath("mentions", "data"))
    user: User


class Transaction(BaseModel):
    """wrapper around Payment returned when you fetch your "stories" feeds"""

    type: TransactionType
    id: str
    note: str
    date_created: datetime
    date_updated: datetime | None
    payment: Payment
    audience: PaymentPrivacy
    device_used: DeviceModel = Field(validation_alias="app")
    comments: list[Comment] = Field(validation_alias=AliasPath("comments", "data"))
