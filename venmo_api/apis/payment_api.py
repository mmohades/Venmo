from venmo_api import ApiClient, Payment, ArgumentMissingError, AlreadyRemindedPaymentError, \
    NoPendingPaymentToUpdateError, NoPaymentMethodFoundError, NotEnoughBalanceError, GeneralPaymentError, \
    User, PaymentMethod, PaymentRole, PaymentPrivacy, deserialize, wrap_callback, get_user_id
from typing import List, Union

from venmo_api.models.eligibility_token import EligibilityToken


class PaymentApi(object):

    def __init__(self, profile, api_client: ApiClient):
        super().__init__()
        self.__profile = profile
        self.__api_client = api_client
        self.__payment_error_codes = {
            "already_reminded_error": 2907,
            "no_pending_payment_error": 2901,
            "no_pending_payment_error2": 2905,
            "not_enough_balance_error": 13006
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
            if response['body']['error']['code'] == self.__payment_error_codes['no_pending_payment_error2']:
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

    def __get_eligibility_token(self, amount: float, note: str, target_id: int = None, funding_source_id: str = None,
                                action: str = "pay",
                                country_code: str = "1", target_type: str = "user_id", callback=None):
        """
        Generate eligibility token which is needed in payment requests
        :param amount: <float> amount of money to be requested
        :param note: <str> message/note of the transaction
        :param target_id: <int> the user id of the person you are sending money to
        :param funding_source_id: <str> Your payment_method id for this payment
        :param action: <str> action that eligibility token is used for
        :param country_code: <str> country code, not sure what this is for
        :param target_type: <str> set by default to user_id, but there are probably other target types
        """
        resource_path = '/protection/eligibility'
        body = {
            "funding_source_id": self.get_default_payment_method().id if not funding_source_id else funding_source_id,
            "action": action,
            "country_code": country_code,
            "target_type": target_type,
            "note": note,
            "target_id": get_user_id(user=None, user_id=target_id),
            "amount": amount,
        }

        response = self.__api_client.call_api(resource_path=resource_path,
                                              body=body,
                                              method='POST')
        if callback:
            return

        return deserialize(response=response, data_type=EligibilityToken)

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
                                          ok_error_codes=list(self.__payment_error_codes.values())[:-1])

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
                                eligibility_token: str = None,
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
        :param eligibility_token:
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
            if not eligibility_token:
                eligibility_token = self.__get_eligibility_token(amount, note, int(target_user_id)).eligibility_token

            body.update({"eligibility_token": eligibility_token})
            body.update({"funding_source_id": funding_source_id})

        resource_path = '/payments'

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=None)

        result = self.__api_client.call_api(resource_path=resource_path,
                                            method='POST',
                                            body=body,
                                            callback=wrapped_callback)
        # handle 200 status code errors
        error_code = result['body']['data'].get('error_code')
        if error_code:
            if error_code == self.__payment_error_codes['not_enough_balance_error']:
                raise NotEnoughBalanceError(amount, target_user_id)

            error = result['body']['data']
            raise GeneralPaymentError(f"{error.get('title')}\n{error.get('error_msg')}")

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
