from venmo_api import JSONSchema, BaseModel
from typing import Dict
from enum import Enum
import logging


class PaymentMethod(BaseModel):
    def __init__(self, pid: str, p_role: str, p_name: str, p_type: str, json=None):
        """
        Payment method model (with different types like, venmo balance, bank account, ...)
        :param pid:
        :param p_role:
        :param p_name:
        :param p_type:
        :param json:
        """
        super().__init__()

        self.id = pid
        self.role = PaymentRole(p_role)
        self.name = p_name
        self.type = payment_type.get(p_type)
        self._json = json

    @classmethod
    def from_json(cls, json: Dict):

        payment_parser = JSONSchema.payment_method(json)

        pid = payment_parser.get_id()
        p_role = payment_parser.get_payment_method_role()
        p_name = payment_parser.get_payment_method_name()
        p_type = payment_parser.get_payment_method_type()

        # Get the class for this payment, must be either VenmoBalance or BankAccount
        payment_class = payment_type.get(p_type)
        if not payment_class:
            logging.warning(f"Skipped a payment_method; No schema existed for the payment_method: {p_type}")
            return

        return payment_class(pid=pid,
                             p_role=p_role,
                             p_name=p_name,
                             p_type=p_type,
                             json=json)


class VenmoBalance(PaymentMethod, BaseModel):
    def __init__(self, pid, p_role, p_name, p_type, json=None):
        super().__init__(pid, p_role, p_name, p_type, json)


class BankAccount(PaymentMethod, BaseModel):
    def __init__(self, pid, p_role, p_name, p_type, json=None):
        super().__init__(pid, p_role, p_name, p_type, json)

class Card(PaymentMethod, BaseModel):
    def __init__(self, pid, p_role, p_name, p_type, json=None):
        super().__init__(pid, p_role, p_name, p_type, json)

class PaymentRole(Enum):
    DEFAULT = 'default'
    BACKUP = 'backup'
    NONE = 'none'


class PaymentPrivacy(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'
    FRIENDS = 'friends'


payment_type = {'bank': BankAccount, 'balance': VenmoBalance, 'card': Card}
