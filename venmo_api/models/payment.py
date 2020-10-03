from enum import Enum

from venmo_api import string_to_timestamp, User, BaseModel
from venmo_api import JSONSchema


class Payment(BaseModel):

    def __init__(self, id_, actor, target, action, amount, audience, date_created, date_reminded, date_completed,
                 note, status):
        """
        Create a Payment object
        :param id_:
        :param actor:
        :param target:
        :param action:
        :param amount:
        :param audience:
        :param date_created:
        :param date_reminded:
        :param date_completed:
        :param note:
        :param status:
        """
        super().__init__()
        self.id = id_
        self.actor = actor
        self.target = target
        self.action = action
        self.amount = amount
        self.audience = audience
        self.date_created = date_created
        self.date_reminded = date_reminded
        self.date_completed = date_completed
        self.note = note
        self.status = status

    @classmethod
    def from_json(cls, json):
        """
        init a new Payment form JSON
        :param json:
        :return:
        """
        if not json:
            return

        parser = JSONSchema.payment(json)

        return cls(
            id_=parser.get_id(),
            actor=User.from_json(parser.get_actor()),
            target=User.from_json(parser.get_target()),
            action=parser.get_action(),
            amount=parser.get_amount(),
            audience=parser.get_amount(),
            date_created=string_to_timestamp(parser.get_date_created()),
            date_reminded=string_to_timestamp(parser.get_date_reminded()),
            date_completed=string_to_timestamp(parser.get_date_completed()),
            note=parser.get_note(),
            status=PaymentStatus(parser.get_status())
        )


class PaymentStatus(Enum):
    SETTLED = 'settled'
    CANCELLED = 'cancelled'
    PENDING = 'pending'
