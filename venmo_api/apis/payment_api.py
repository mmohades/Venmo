from venmo_api import ApiClient
from venmo_api import User, PaymentMethod, PaymentRole, PaymentPrivacy
from venmo_api import NoPaymentMethodFoundError
from venmo_api import deserialize, wrap_callback, get_user_id
from typing import List, Union


class PaymentApi(object):

    def __init__(self, api_client: ApiClient):
        super().__init__()
        self.__api_client = api_client

    def get_payment_methods(self, callback=None) -> Union[List[PaymentMethod], None]:
        """
        Get a list of available payment_methods
        :param callback:
        :return:
        """

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=PaymentMethod)

        resource_path = '/payment-methods'
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET',
                                              callback=wrapped_callback)
        # return the thread
        if callback:
            return

        return deserialize(response=response, data_type=PaymentMethod)

    def send_money(self, amount: float,
                   note: str,
                   target_user_id: int = None,
                   funding_source_id: str = None,
                   target_user: User = None,
                   privacy_setting: PaymentPrivacy = PaymentPrivacy.PRIVATE,
                   callback=None) -> Union[bool, None]:
        """
        send [amount] money with [note] to the ([target_user_id] or [target_user]) from the [funding_source_id]
        If no [funding_source_id] is provided, it will find the default source_id and uses that.
        :param amount: <float>
        :param note: <str>
        :param funding_source_id: <str> Your payment_method id for this payment
        :param privacy_setting: <PaymentPrivacy> PRIVATE/FRIENDS/PUBLIC (enum)
        :param target_user_id: <str>
        :param target_user: <User>
        :param callback: <function> Passing callback will run it in a distinct thread, and returns Thread
        :return: <bool> Either the transaction was successful or an exception will rise.
        """

        return self.__send_or_request_money(amount=amount,
                                            note=note,
                                            is_send_money=True,
                                            funding_source_id=funding_source_id,
                                            privacy_setting=privacy_setting.value,
                                            target_user_id=target_user_id,
                                            target_user=target_user,
                                            callback=callback)

    def request_money(self, amount: float,
                      note: str,
                      target_user_id: int = None,
                      privacy_setting: PaymentPrivacy = PaymentPrivacy.PRIVATE,
                      target_user: User = None,
                      callback=None) -> Union[bool, None]:
        """
        Request [amount] money with [note] from the ([target_user_id] or [target_user])
        :param amount: <float> amount of money to be requested
        :param note: <str> message/note of the transaction
        :param privacy_setting: <PaymentPrivacy> PRIVATE/FRIENDS/PUBLIC (enum)
        :param target_user_id: <str> the user id of the person you are asking the money from
        :param target_user: <User> The user object or user_id is required
        :param callback: callback function
        :return: <bool> Either the transaction was successful or an exception will rise.
        """
        return self.__send_or_request_money(amount=amount,
                                            note=note,
                                            is_send_money=False,
                                            funding_source_id=None,
                                            privacy_setting=privacy_setting.value,
                                            target_user_id=target_user_id,
                                            target_user=target_user,
                                            callback=callback)

    def __send_or_request_money(self, amount: float,
                                note: str,
                                is_send_money,
                                funding_source_id: str = None,
                                privacy_setting: str = PaymentPrivacy.PRIVATE.value,
                                target_user_id: int = None, target_user: User = None,
                                callback=None) -> Union[bool, None]:
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
        target_user_id = str(get_user_id(target_user, target_user_id))

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

        self.__api_client.call_api(resource_path=resource_path,
                                   method='POST',
                                   body=body,
                                   callback=wrapped_callback)
        if callback:
            return
        # if no exception raises, then it was successful
        return True

    def get_default_payment_method(self) -> PaymentMethod:
        """
        Search in all payment_methods and find the one that has payment_role of Default
        :return:
        """
        payment_methods = self.get_payment_methods()

        for p_method in payment_methods:
            if p_method.role == PaymentRole.DEFAULT:
                return p_method

        raise NoPaymentMethodFoundError()
