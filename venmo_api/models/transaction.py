from venmo_api import string_to_timestamp, BaseModel, User, Comment, get_phone_model_from_json, JSONSchema
from enum import Enum


class Transaction(BaseModel):

    def __init__(self, story_id, payment_id, date_completed, date_created,
                 date_updated, payment_type, amount, audience, status,
                 note, device_used, actor, target, comments, json=None):
        """
        Transaction model
        :param story_id:
        :param payment_id:
        :param date_completed:
        :param date_created:
        :param date_updated:
        :param payment_type:
        :param amount:
        :param audience:
        :param status:
        :param note:
        :param device_used:
        :param actor:
        :param target:
        :param comments:
        :param json:
        """
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
        self.comments = comments

        self.actor = actor
        self.target = target
        self._json = json

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

        comments_list = parser.get_comments()
        comments = [Comment.from_json(json=comment) for comment in comments_list] if comments_list else []

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
                   target=target,
                   comments=comments,
                   json=json)


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
