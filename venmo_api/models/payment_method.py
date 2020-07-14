from typing import Dict
from enum import Enum
from venmo_api import JSONSchema


class PaymentMethod(object):
    def __init__(self, pid: str, p_role: str, p_name: str, p_type: str):
        super().__init__()

        self.id = pid
        self.role = PaymentRole(p_role)
        self.name = p_name
        self.type = payment_type.get(p_type)

    @classmethod
    def from_json(cls, json: Dict):

        payment_parser = JSONSchema.payment_method(json)

        pid = payment_parser.get_id()
        p_role = payment_parser.get_payment_method_role()
        p_name = payment_parser.get_payment_method_name()
        p_type = payment_parser.get_payment_method_type()

        # Get the class for this payment, must be either VenmoBalance or BankAccount
        payment_class = payment_type[p_type]

        return payment_class(pid=pid,
                             p_role=p_role,
                             p_name=p_name,
                             p_type=p_type)

    def __str__(self):
        return f"Payment: id: {self.id}, role: {self.role}, name: {self.name}, type: {self.type}"


class VenmoBalance(PaymentMethod):
    def __init__(self, pid, p_role, p_name, p_type):
        super().__init__(pid, p_role, p_name, p_type)


class BankAccount(PaymentMethod):
    def __init__(self, pid, p_role, p_name, p_type):
        super().__init__(pid, p_role, p_name, p_type)


class PaymentRole(Enum):
    DEFAULT = 'default'
    BACKUP = 'backup'
    NONE = 'none'


class PaymentPrivacy(Enum):
    PRIVATE = 'private'
    PUBLIC = 'public'
    FRIENDS = 'friends'


payment_type = {'bank': BankAccount, 'balance': VenmoBalance}
