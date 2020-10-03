from enum import Enum
from venmo_api import string_to_timestamp, BaseModel
from venmo_api import User
from venmo_api import get_phone_model_from_json
from venmo_api import JSONSchema


class Transaction(BaseModel):

    def __init__(self, story_id, payment_id, date_completed, date_created,
                 date_updated, payment_type, amount, audience, status,
                 note, device_used, actor, target):

        super().__init__()

        self.id = story_id
        self.payment_id = payment_id

        self.date_completed = date_completed
        self.date_created = date_created
        self.date_updated = date_updated

        self.payment_type = payment_type
        self.amount = amount
        self.audience = audience
        self.status = status

        self.note = note
        self.device_used = device_used

        self.actor = actor
        self.target = target

    @classmethod
    def from_json(cls, json):
        """
        Create a new Transaction from the given json.
        This only works for transactions, skipping refunds and bank transfers.
        :param json:
        :return:
        """

        if not json:
            return

        parser = JSONSchema.transaction(json)
        transaction_type = TransactionType(parser.get_transaction_type())

        # Currently only handles Payment-type transactions
        if transaction_type is not TransactionType.PAYMENT:
            return

        date_created = string_to_timestamp(parser.get_date_created())
        date_updated = string_to_timestamp(parser.get_date_updated())
        date_completed = string_to_timestamp(parser.get_date_completed())
        target = User.from_json(json=parser.get_target())
        actor = User.from_json(json=parser.get_actor())
        device_used = get_phone_model_from_json(parser.get_actor_app())

        return cls(story_id=parser.get_story_id(),
                   payment_id=parser.get_payment_id(),
                   date_completed=date_completed,
                   date_created=date_created,
                   date_updated=date_updated,
                   payment_type=parser.get_type(),
                   amount=parser.get_amount(),
                   audience=parser.get_audience(),
                   note=parser.get_story_note(),
                   status=parser.get_status(),
                   device_used=device_used,
                   actor=actor,
                   target=target)


class TransactionType(Enum):
    PAYMENT = 'payment'
    # merchant refund
    REFUND = 'refund'
    # to/from bank account
    TRANSFER = 'transfer'
    # add money to debit card
    TOP_UP = 'top_up'
    # debit card purchase
    AUTHORIZATION = 'authorization'
    # debit card atm withdrawal
    ATM_WITHDRAWAL = 'atm_withdrawal'

    DISBURSEMENT = 'disbursement'

