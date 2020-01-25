from api_client import ApiClient
from models import User, PaymentMethod, PaymentRole, PaymentPrivacy
from models.exception import ArgumentMissingError, NoPaymentMethodFoundError
from utils import deserialize, wrap_callback
from typing import List


class PaymentApi(object):

    def __init__(self, api_client: ApiClient):
        super().__init__()
        self.__api_client = api_client

    def get_payment_methods(self, callback=None) -> List[PaymentMethod]:

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=PaymentMethod)

        resource_path = '/payment-methods'
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET',
                                              callback=wrapped_callback)
        # return the thread
        if callback:
            return response

        return deserialize(response=response, data_type=User)

    def make_a_payment(self, amount: float,
                       note: str,
                       funding_source_id: str,
                       privacy_setting: str = PaymentPrivacy.private,
                       target_user_id: int = None, target_user: User = None):
        """

        :param amount:
        :param note:
        :param funding_source_id: <str> Your payment_method id for this payment
        :param privacy_setting: <str> private/friends/public
        :param target_user_id:
        :param target_user:
        :return:
        """

        if not target_user and not target_user_id:
            raise ArgumentMissingError(arguments=('target_user_id', 'target_user'))

        if not funding_source_id:
            funding_source_id = self.get_default_payment_method().id

        resource_path = '/payments'

        body = {
            "funding_source_id": funding_source_id,
            "metadata": {
                "quasi_cash_disclaimer_viewed": False
            },
            "user_id": target_user_id,
            "audience": privacy_setting,
            "amount": amount,
            "note": note
        }

        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='POST',
                                              body=body)
        print(response['body'])

        # TODO: Return the response? Maybe return true or false would be enough

    def request_money(self, amount: float,
                      note: str,
                      privacy_setting: str = PaymentPrivacy.private,
                      target_user_id: int = None, target_user: User = None):

        if not target_user and not target_user_id:
            raise ArgumentMissingError(arguments=('target_user_id', 'target_user'))
        amount = -abs(amount)

        resource_path = '/payments'

        body = {
            "metadata": {
                "quasi_cash_disclaimer_viewed": False
            },
            "user_id": target_user_id,
            "audience": privacy_setting,
            "amount": amount,
            "note": note
        }

        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='POST',
                                              body=body)

        print(response['body'])

    def get_default_payment_method(self):
        payment_methods = self.get_payment_methods()

        for p_method in payment_methods:
            if p_method.role == PaymentRole.default:
                return p_method

        raise NoPaymentMethodFoundError()

    def __make_or_request_money(self, amount: float, note: str, send_money: bool,
                                target_user_id: int):

        if not send_money:
            amount = -amount

        body = {
          "note": note,
          "metadata": {
            "quasi_cash_disclaimer_viewed": False
          },
          "amount": amount,
          "user_id": target_user_id,
          "audience": "private"
        }

