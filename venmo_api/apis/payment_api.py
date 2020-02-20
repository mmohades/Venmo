from venmo_api import ApiClient
from venmo_api import User, PaymentMethod, PaymentRole, PaymentPrivacy
from venmo_api import ArgumentMissingError, NoPaymentMethodFoundError
from venmo_api import deserialize, wrap_callback
from threading import Thread
from typing import List, Union


class PaymentApi(object):

    def __init__(self, api_client: ApiClient):
        super().__init__()
        self.__api_client = api_client

    def get_payment_methods(self, callback=None) -> Union[List[PaymentMethod], Thread]:

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
                   callback=None) -> Union[bool, Thread]:
        """
        :param amount: <float>
        :param note: <str>
        :param funding_source_id: <str> Your payment_method id for this payment
        :param privacy_setting: <str> private/friends/public
        :param target_user_id: <str>
        :param target_user: <User>
        :param callback: <function> Passing callback will run it in a distinct thread, and returns Thread
        :return: <bool> Either the transaction was successful or an exception will rise.
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
                      target_user_id: int = None, target_user: User = None,
                      privacy_setting: str = PaymentPrivacy.private.value,
                      callback=None) -> Union[bool, Thread]:
        """
        Request money from a user.
        :param amount: <float> amount of money to be requested
        :param note: <str> message/note of the transaction
        :param privacy_setting: <str> private/friends/public (enum)
        :param target_user_id: <str> the user id of the person you are asking the money from
        :param target_user: <User> The user object or user_id is required
        :param callback: callback function
        :return: <bool> Either the transaction was successful or an exception will rise.
        """
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
                                callback=None) -> Union[bool, Thread]:
        """
        Generic method for sending and requesting money
        :param amount:
        :param note:
        :param is_send_money:
        :param funding_source_id:
        :param privacy_setting:
        :param target_user_id:
        :param target_user:
        :param callback:
        :return:
        """
        if not target_user and not target_user_id:
            raise ArgumentMissingError(arguments=('target_user_id', 'target_user'))

        amount = abs(amount)
        if not is_send_money:
            amount = -amount

        body = {
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

    def get_default_payment_method(self) -> PaymentMethod:
        """
        Search in all payment_methods and find the one that has payment_role of Default
        :return:
        """
        payment_methods = self.get_payment_methods()

        for p_method in payment_methods:
            if p_method.role == PaymentRole.default:
                return p_method

        raise NoPaymentMethodFoundError()
