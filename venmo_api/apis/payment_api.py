from venmo_api import ApiClient, Payment, ArgumentMissingError, AlreadyRemindedPaymentError, \
    NoPendingPaymentToUpdateError
from venmo_api import User, PaymentMethod, PaymentRole, PaymentPrivacy
from venmo_api import NoPaymentMethodFoundError
from venmo_api import deserialize, wrap_callback, get_user_id
from typing import List, Union


class PaymentApi(object):

    def __init__(self, profile, api_client: ApiClient):
        super().__init__()
        self.__profile = profile
        self.__api_client = api_client
        self.__payment_update_error_codes = {
            "already_reminded_error": 2907,
            "no_pending_payment_error": 2901,
            "no_pending_payment_error2": 2905
        }

    def get_charge_payments(self, limit=100000, callback=None):
        """
        Get a list of charge ongoing payments (pending request money)
        :param limit:
        :param callback:
        :return:
        """
        return self.__get_payments(action="charge",
                                   limit=limit,
                                   callback=callback)

    def get_pay_payments(self, limit=100000, callback=None):
        """
        Get a list of pay ongoing payments (pending requested money from your profile)
        :param limit:
        :param callback:
        :return:
        """
        return self.__get_payments(action="pay",
                                   limit=limit,
                                   callback=callback)

    def remind_payment(self, payment: Payment = None, payment_id: int = None) -> bool:
        """
        Send a reminder for payment/payment_id
        :param payment: either payment object or payment_id must be be provided
        :param payment_id:
        :return: True or raises AlreadyRemindedPaymentError
        """

        # if the reminder has already sent
        payment_id = payment_id or payment.id
        action = 'remind'

        response = self.__update_payment(action=action,
                                         payment_id=payment_id)

        # if the reminder has already sent
        if 'error' in response.get('body'):
            if response['body']['error']['code'] == self.__payment_update_error_codes['no_pending_payment_error2']:
                raise NoPendingPaymentToUpdateError(payment_id=payment_id,
                                                    action=action)
            raise AlreadyRemindedPaymentError(payment_id=payment_id)
        return True

    def cancel_payment(self, payment: Payment = None, payment_id: int = None) -> bool:
        """
        Cancel the payment/payment_id provided. Only applicable to payments you have access to (requested payments)
        :param payment:
        :param payment_id:
        :return: True or raises NoPendingPaymentToCancelError
        """
        # if the reminder has already sent
        payment_id = payment_id or payment.id
        action = 'cancel'

        response = self.__update_payment(action=action,
                                         payment_id=payment_id)

        if 'error' in response.get('body'):
            raise NoPendingPaymentToUpdateError(payment_id=payment_id,
                                                action=action)
        return True

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

    def __update_payment(self, action, payment_id):

        if not payment_id:
            raise ArgumentMissingError(arguments=('payment', 'payment_id'))

        resource_path = f'/payments/{payment_id}'
        body = {
            "action": action,
        }
        return self.__api_client.call_api(resource_path=resource_path,
                                          body=body,
                                          method='PUT',
                                          ok_error_codes=list(self.__payment_update_error_codes.values()))

    def __get_payments(self, action, limit, callback=None):
        """
        Get a list of ongoing payments with the given action
        :return:
        """
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=Payment)

        resource_path = '/payments'
        parameters = {
            "action": action,
            "actor": self.__profile.id,
            "limit": limit
        }
        response = self.__api_client.call_api(resource_path=resource_path,
                                              params=parameters,
                                              method='GET',
                                              callback=wrapped_callback)
        if callback:
            return

        return deserialize(response=response, data_type=Payment)

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
            if not p_method:
                continue

            if p_method.role == PaymentRole.DEFAULT:
                return p_method

        raise NoPaymentMethodFoundError()
