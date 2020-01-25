from typing import Dict
from enum import Enum


class PaymentMethod:
    def __init__(self, pid: str, p_role: str, p_name: str, p_type: str):
        self.id = pid
        self.role = PaymentRole(p_role)
        self.name = p_name
        self.type = payment_type.get(p_type)

    @classmethod
    def from_json(cls, json: Dict):
        pid = json.get(p_format['id'])
        p_role = json.get(p_format['payment_role'])
        p_name = json.get(p_format['name'])
        p_type = json.get(p_format['type'])

        # Get the class for this payment, must be either VenmoBalance or BankAccount
        payment_class = payment_type[p_type]

        return payment_class(pid=pid,
                             p_role=p_role,
                             p_name=p_name,
                             p_type=p_type)

    def __str__(self):
        return f"id: {self.id}, payment_role: {self.role}, payment_name: {self.name}, type: {self.type}"


class VenmoBalance(PaymentMethod):
    def __init__(self, pid, p_role, p_name, p_type):
        super().__init__(pid, p_role, p_name, p_type)


class BankAccount(PaymentMethod):
    def __init__(self, pid, p_role, p_name, p_type):
        super().__init__(pid, p_role, p_name, p_type)


class PaymentRole(Enum):
    default = 'default'
    backup = 'backup'
    none = 'none'


class PaymentPrivacy(Enum):

    private = 'private'
    public = 'public'
    friends = 'friends'


payment_type = {'bank': BankAccount, 'balance': VenmoBalance}

p_format = {'id': 'id',
            'payment_role': 'peer_payment_role',
            'name': 'name',
            'type': 'type'}
