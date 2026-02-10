from datetime import datetime
from enum import StrEnum, auto
from typing import Annotated, Any, Literal

from pydantic import AfterValidator, AliasPath, BaseModel, Field

from venmo_api.models.user import PaymentPrivacy, User

UsDollarsFloat = Annotated[float, AfterValidator(lambda v: round(v, 2))]


# ---  ENUMS ---
class PaymentStatus(StrEnum):
    SETTLED = auto()
    CANCELLED = auto()
    PENDING = auto()
    HELD = auto()
    FAILED = auto()
    EXPIRED = auto()


class PaymentAction(StrEnum):
    PAY = auto()
    CHARGE = auto()


class PaymentMethodRole(StrEnum):
    DEFAULT = auto()
    BACKUP = auto()
    NONE = auto()


class PaymentMethodType(StrEnum):
    BANK = auto()
    BALANCE = auto()
    CARD = auto()


# --- MODELS ---


class Fee(BaseModel):
    """bundled with EligilityToken and PaymentMethod responses. I don't pay fees so IDK
    really what's up there."""

    product_uri: str
    applied_to: str
    base_fee_amount: UsDollarsFloat
    fee_percentage: float
    calculated_fee_amount_in_cents: int
    fee_token: str


class EligibilityToken(BaseModel):
    """required for sending payments"""

    eligibility_token: str
    eligible: bool
    fees: list[Fee]
    fee_disclaimer: str
    ineligible_reason: str | None = Field(
        None,
        description="If your eligibility is denied, you'll get this cryptic string.",
    )


class Payment(BaseModel):
    """object returned by a successful payment/request"""

    id: str
    status: PaymentStatus
    action: PaymentAction
    amount: UsDollarsFloat | None
    date_created: datetime
    audience: PaymentPrivacy | None = None
    note: str
    target: User = Field(validation_alias=AliasPath("target", "user"))
    actor: User
    date_completed: datetime | None
    date_reminded: datetime | None
    # TODO figure these out
    refund: Any | None = None
    fee: Fee | None = None


class PaymentMethod(BaseModel):
    id: str
    type: PaymentMethodType
    name: str
    last_four: str | None
    peer_payment_role: PaymentMethodRole
    merchant_payment_role: PaymentMethodRole
    top_up_role: Literal["eligible", "none"]
    default_transfer_destination: Literal["default", "eligible", "none"]
    fee: Fee | None
    # TODO maybe bank_account: BankAccount | None
    # card: Card | None
    # add_funds_eligible: bool,
    # is_preferred_payment_method_for_add_funds: bool


class TransferDestination(BaseModel):
    """variant of PaymentMethod specifically for transfers to/from your Venmo balance"""

    id: int
    type: PaymentMethodType
    name: str
    last_four: str | None
    is_default: bool
    transfer_to_estimate: datetime
    account_status: Literal["verified"] | Any


class TransferPostResponse(BaseModel):
    """object returned by a successful transfer"""

    id: int
    amount: UsDollarsFloat
    amount_cents: int
    amount_fee_cents: int
    amount_requested_cents: int
    date_requested: datetime
    destination: TransferDestination
    status: Literal["pending"]
    type: Literal["standard", "instant"]
