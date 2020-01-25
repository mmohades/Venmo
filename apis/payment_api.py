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

        return deserialize(response=response, data_type=PaymentMethod)

    def send_money(self, amount: float,
                   note: str,
                   funding_source_id: str = None,
                   privacy_setting: str = PaymentPrivacy.private.value,
                   target_user_id: int = None, target_user: User = None,
                   callback=None):
        """
        :param amount: <float>
        :param note: <str>
        :param funding_source_id: <str> Your payment_method id for this payment
        :param privacy_setting: <str> private/friends/public
        :param target_user_id: <str>
        :param target_user: <User>
        :param callback: <function>
        :return:
        """

        return self.__send_or_request_money(amount=amount,
                                            note=note,
                                            is_send_money=True,
                                            funding_source_id=funding_source_id,
                                            privacy_setting=privacy_setting,
                                            target_user_id=target_user_id,
                                            target_user=target_user,
                                            callback=callback)

    def request_money(self, amount: float,
                      note: str,
                      privacy_setting: str = PaymentPrivacy.private.value,
                      target_user_id: int = None, target_user: User = None,
                      callback=None):

        return self.__send_or_request_money(amount=amount,
                                            note=note,
                                            is_send_money=False,
                                            funding_source_id=None,
                                            privacy_setting=privacy_setting,
                                            target_user_id=target_user_id,
                                            target_user=target_user,
                                            callback=callback)

    def __send_or_request_money(self, amount: float,
                                note: str,
                                is_send_money,
                                funding_source_id: str = None,
                                privacy_setting: str = PaymentPrivacy.private.value,
                                target_user_id: int = None, target_user: User = None,
                                callback=None):

        if not target_user and not target_user_id:
            raise ArgumentMissingError(arguments=('target_user_id', 'target_user'))

        amount = abs(amount)
        if not is_send_money:
            amount = -amount

        body = {
            "metadata": {
                "quasi_cash_disclaimer_viewed": False
            },
            "user_id": target_user_id,
            "audience": privacy_setting,
            "amount": amount,
            "note": note
        }

        if is_send_money:
            if not funding_source_id:
                funding_source_id = self.get_default_payment_method().id
            body.update({"funding_source_id": funding_source_id})

        resource_path = '/payments'

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=None)

        threaded = self.__api_client.call_api(resource_path=resource_path,
                                              method='POST',
                                              body=body,
                                              callback=wrapped_callback)
        if callback:
            return threaded
        # if no exception raises, then it was successful
        return True

    def get_default_payment_method(self):
        payment_methods = self.get_payment_methods()

        for p_method in payment_methods:
            print(p_method)
            if p_method.role == PaymentRole.default:
                return p_method

        raise NoPaymentMethodFoundError()
