import uuid
from typing import Literal

from venmo_api.apis.api_client import ApiClient
from venmo_api.apis.api_util import ValidatedResponse, deserialize
from venmo_api.apis.exception import (
    AlreadyRemindedPaymentError,
    GeneralPaymentError,
    NoPaymentMethodFoundError,
    NoPendingPaymentToUpdateError,
    NotEnoughBalanceError,
)
from venmo_api.models.page import Page
from venmo_api.models.payment import (
    EligibilityToken,
    Payment,
    PaymentAction,
    PaymentMethod,
    PaymentMethodRole,
    TransferDestination,
    TransferPostResponse,
)
from venmo_api.models.user import PaymentPrivacy, User


class PaymentApi:
    """
    API for querying and making/requesting payments.

    Args:
        profile (User): User object for the current user, fetched at login.
        api_client (ApiClient): Logged in client instance to use for requests.
        balance (float | None, optional): User initial Venmo balance, if desired. Defaults
            to None.
    """

    def __init__(
        self, profile: User, api_client: ApiClient, balance: float | None = None
    ):
        self._profile = profile
        self._balance = balance
        self._api_client = api_client
        self._payment_error_codes = {
            "already_reminded_error": 2907,
            "no_pending_payment_error": 2901,
            "no_pending_payment_error2": 2905,
            "not_enough_balance_error": 13006,
            "otp_step_up_required_error": 1396,
        }

    def get_charge_payments(self, limit=100000) -> Page[Payment]:
        """Get a list of charge ongoing payments (pending request money)

        Args:
            limit (int, optional): Maximum number of payments to fetch. Defaults to 100000.

        Returns:
            Page[Payment]
        """
        return self._get_payments(action="charge", limit=limit)

    def get_pay_payments(self, limit=100000) -> Page[Payment]:
        """Get a list of pay ongoing payments (pending requested money from your profile)

        Args:
            limit (int, optional): Maximum number of payments to fetch. Defaults to 100000.

        Returns:
            Page[Payment]
        """
        return self._get_payments(action="pay", limit=limit)

    def remind_payment(self, payment_id: str) -> bool:
        """Send a reminder for a payment

        Args:
            payment_id (str): the uuid for the payment, as returned by Payment.id.

        Raises:
            NoPendingPaymentToUpdateError
            AlreadyRemindedPaymentError

        Returns:
            bool: True or raises AlreadyRemindedPaymentError
        """
        action = "remind"
        response = self._update_payment(action=action, payment_id=payment_id)

        # if the reminder has already sent
        if "error" in response.body:
            if (
                response.body["error"]["code"]
                == self._payment_error_codes["no_pending_payment_error2"]
            ):
                raise NoPendingPaymentToUpdateError(payment_id, action)
            raise AlreadyRemindedPaymentError(payment_id=payment_id)
        return True

    def cancel_payment(self, payment_id: str) -> bool:
        """Cancel the payment_id provided. Only applicable to payments you have access
        to (requested payments).

        Args:
            payment_id (str): the uuid for the payment

        Raises:
            NoPendingPaymentToUpdateError

        Returns:
            bool:  True or raises NoPendingPaymentToCancelError
        """
        action = "cancel"
        response = self._update_payment(action=action, payment_id=payment_id)
        if "error" in response.body:
            raise NoPendingPaymentToUpdateError(payment_id, action)
        return True

    def get_payment_methods(self) -> Page[PaymentMethod]:
        """
        Get a list of available payment_methods
        """
        response = self._api_client.call_api(
            resource_path="/payment-methods", method="GET"
        )
        return deserialize(response=response, data_type=PaymentMethod)

    def send_money(
        self,
        amount: float,
        note: str,
        target_user_id: str,
        funding_source_id: str = None,
        privacy_setting: PaymentPrivacy = PaymentPrivacy.PRIVATE,
    ) -> Payment:
        """send [amount] money with [note] to the ([target_user_id] from the [funding_source_id]
        If no [funding_source_id] is provided, it will find the default source_id and uses that.

        Args:
            amount (float): Amount in US dollars, gets rounded to 2 decimals internally.
            note (str): descriptive note required with payment.
            target_user_id (str): uuid of recipient user, as returned by User.id.
            funding_source_id (str, optional): uuid of funding source. Defaults to None.
            privacy_setting (PaymentPrivacy, optional): PRIVATE/FRIENDS/PUBLIC .
                Defaults to PaymentPrivacy.PRIVATE.

        Returns:
            Payment: Either the transaction was successful or an exception will rise.
        """
        return self._send_or_request_money(
            amount=amount,
            note=note,
            is_send_money=True,
            funding_source_id=funding_source_id,
            target_user_id=target_user_id,
            privacy_setting=privacy_setting.value,
        )

    def request_money(
        self,
        amount: float,
        note: str,
        target_user_id: str,
        privacy_setting: PaymentPrivacy = PaymentPrivacy.PRIVATE,
    ) -> Payment:
        """Request [amount] money with [note] from  [target_user_id].

        Args:
            amount (float): Amount in US dollars, gets rounded to 2 decimals internally.
            note (str): descriptive note required with payment.
            target_user_id (str): uuid of recipient user, as returned by User.id.
            privacy_setting (PaymentPrivacy, optional): PRIVATE/FRIENDS/PUBLIC .
                Defaults to PaymentPrivacy.PRIVATE.

        Returns:
            Payment: Either the transaction was successful or an exception will rise.
        """
        return self._send_or_request_money(
            amount=amount,
            note=note,
            is_send_money=False,
            funding_source_id=None,
            target_user_id=target_user_id,
            privacy_setting=privacy_setting.value,
        )

    def get_transfer_destinations(
        self, trans_type: Literal["standard", "instant"]
    ) -> Page[TransferDestination]:
        """Get a list of available transfer destination options from your Venmo balance
        for the given type.

        Args:
            trans_type (Literal[&quot;standard&quot;, &quot;instant&quot;]): 'standard' is
                the free transfer that takes longer, 'instant' is the quicker transfer
                that charges a fee.

        Returns:
            Page[TransferDestination]: list of eligible destinations.
        """
        response = self._api_client.call_api(
            resource_path="/transfers/options", method="GET"
        )
        return deserialize(
            response, TransferDestination, [trans_type, "eligible_destinations"]
        )

    def initiate_transfer(
        self,
        destination_id: str,
        amount: float | None = None,
        trans_type: Literal["standard", "instant"] = "standard",
    ) -> TransferPostResponse:
        """Initiate a transfer from your Venmo balance.

        Args:
            destination_id (str): uuid of transfer destination, as returned by
                TransferDestination.id.
            amount (float | None, optional): Amount in US dollars, gets rounded to 2
                decimals internally. Defaults to None, in which case the entire Venmo
                balance determined at initialization is used.
            trans_type (Literal[&quot;standard&quot;, &quot;instant&quot;], optional):
                'standard' is the free transfer that takes longer, 'instant' is the
                quicker transfer that charges a fee. Defaults to "standard".

        Raises:
            ValueError

        Returns:
            TransferPostResponse: object signifying successful transfer with details.
        """
        if amount is None:
            if self._balance is not None:
                amount = self._balance
            else:
                raise ValueError("must pass a transfer amount if no balance available")

        amount_cents = round(amount * 100)
        body = {
            "amount": amount_cents,
            "destination_id": destination_id,
            "transfer_type": trans_type,
            # TODO should this have a fee subtracted? don't feel like testing
            "final_amount": amount_cents,
        }
        response = self._api_client.call_api(
            resource_path="/transfers", body=body, method="POST"
        )
        return deserialize(response, TransferPostResponse)

    def get_default_payment_method(self) -> PaymentMethod:
        """
        Search in all payment_methods and find the one that has payment_role of Default
        """
        payment_methods = self.get_payment_methods()

        for p_method in payment_methods:
            if not p_method:
                continue

            if p_method.peer_payment_role == PaymentMethodRole.DEFAULT:
                return p_method

        raise NoPaymentMethodFoundError()

    # --- HELPERS ---

    def _get_eligibility_token(
        self,
        amount: float,
        note: str,
        target_id: str,
        action: str = "pay",
        country_code: str = "1",
        target_type: str = "user_id",
    ) -> EligibilityToken:
        """Generate eligibility token which is needed in payment requests

        Args:
            amount (float): Amount in US dollars, gets rounded to 2 decimals internally.
            note (str): descriptive note required with payment.
            target_id (str): uuid of recipient user, as returned by User.id.
            action (str, optional): "pay" is currently the only valid argument observed.
                Defaults to "pay".
            country_code (str, optional): "1" is currently the only valid argument
                observed. Defaults to "1", presumably for USA.
            target_type (str, optional): "user_id" is currently the only valid argument
                observed. Defaults to "user_id".

        Returns:
            EligibilityToken: ephemeral token that must be passed in payment payload.
        """
        body = {
            "funding_source_id": "",  # api leaves this blank currently
            "action": action,
            "country_code": country_code,
            "target_type": target_type,
            "note": note,
            "target_id": target_id,
            "amount": round(amount * 100),
        }
        response = self._api_client.call_api(
            resource_path="/protection/eligibility", body=body, method="POST"
        )
        return deserialize(response=response, data_type=EligibilityToken)

    def _update_payment(
        self, action: Literal["remind", "cancel"], payment_id: str
    ) -> ValidatedResponse:
        return self._api_client.call_api(
            resource_path=f"/payments/{payment_id}",
            body={"action": action},
            method="PUT",
            ok_error_codes=list(self._payment_error_codes.values())[:-1],
        )

    def _get_payments(self, action: PaymentAction, limit: int) -> Page[Payment]:
        """
        Helper method for getting a list of ongoing payments with the given action
        """
        parameters = {"action": action, "actor": self._profile.id, "limit": limit}
        # TODO other params `status: pending,held`
        response = self._api_client.call_api(
            resource_path="/payments",
            params=parameters,
            method="GET",
        )
        return deserialize(response=response, data_type=Payment)

    def _send_or_request_money(
        self,
        amount: float,
        note: str,
        is_send_money: bool,
        funding_source_id: str,
        target_user_id: str,
        privacy_setting: PaymentPrivacy = PaymentPrivacy.PRIVATE,
        eligibility_token: str | None = None,
    ) -> Payment:
        """
        Helper method for sending and requesting money.
        """

        amount = abs(amount)
        if not is_send_money:
            amount = -amount

        body = {
            "uuid": str(uuid.uuid4()),
            "user_id": target_user_id,
            "audience": privacy_setting,
            "amount": round(amount, 2),
            "note": note,
        }

        if is_send_money:
            if not funding_source_id:
                funding_source_id = self.get_default_payment_method().id
            if not eligibility_token:
                eligibility_token = self._get_eligibility_token(
                    amount, note, target_user_id
                ).eligibility_token
            body.update({"eligibility_token": eligibility_token})
            body.update({"funding_source_id": funding_source_id})

        response = self._api_client.call_api(
            resource_path="/payments",
            method="POST",
            body=body,
            ok_error_codes=[
                self._payment_error_codes["otp_step_up_required_error"],
                self._payment_error_codes["not_enough_balance_error"],
            ],
        )

        # handle 200 status code errors
        error_code = None
        try:
            error_code = response.body.get("error").get("code")
        except:
            pass

        if error_code:
            if error_code == self._payment_error_codes["otp_step_up_required_error"]:
                raise RuntimeError(
                    "OTP step-up required for payment to go through, log out and try "
                    "again on an actual device."
                )

            elif error_code == self._payment_error_codes["not_enough_balance_error"]:
                raise NotEnoughBalanceError(amount, target_user_id)

            error = response.body["data"]
            raise GeneralPaymentError(f"{error.get('title')}\n{error.get('error_msg')}")

        # if no exception raises, then it was successful
        return deserialize(response, Payment, nested_response=["payment"])
