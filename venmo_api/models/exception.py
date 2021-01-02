from json import JSONDecodeError


# ======= Authentication Exceptions =======

class AuthenticationFailedError(Exception):
    """Raised when there is an invalid argument passed into a method"""

    def __init__(self, msg: str = None, reason: str = None):
        self.msg = msg or f"Authentication failed. " + reason or ""
        super(AuthenticationFailedError, self).__init__(self.msg)


# ======= HTTP Requests Exceptions =======

class InvalidHttpMethodError(Exception):
    """HTTP Method must be POST, PUT, GET or DELETE in a string format"""

    def __init__(self, msg: str = None):
        self.msg = msg or "Method is not valid. Method must be POST, PUT, GET or DELETE in a string format"
        super(InvalidHttpMethodError, self).__init__(self.msg)


class ResourceNotFoundError(Exception):
    """Raise it for 400 HTTP status code, when resource is not found"""

    def __init__(self, msg: str = None):
        self.msg = msg or "400 Bad Request. Couldn't find the requested resource."
        super(ResourceNotFoundError, self).__init__(self.msg)


class HttpCodeError(Exception):
    """When status code is anything except 400 and 200s"""
    def __init__(self, response=None, msg: str = None):
        if response is None and msg is None:
            raise Exception("Neither response nor message for creating HttpCodeError was passed.")
        status_code = response.status_code or "NA"
        reason = response.reason or "Unknown reason"
        try:
            json = response.json()
        except JSONDecodeError:
            json = "Invalid Json"

        self.msg = msg or f"HTTP Status code is invalid. Could not make the request because -> "\
            f"{status_code} {reason}.\nError: {json}"

        super(HttpCodeError, self).__init__(self.msg)


# ======= Methods Exceptions =======

class InvalidArgumentError(Exception):
    """Raised when there is an invalid argument passed into a method"""

    def __init__(self, msg: str = None, argument_name: str = None, reason=None):
        self.msg = msg or f"Invalid argument {argument_name} was passed. " + (reason or "")
        super(InvalidArgumentError, self).__init__(self.msg)


class ArgumentMissingError(Exception):
    """Raised when there is an argument missing in a function"""

    def __init__(self, msg: str = None, arguments: tuple = None, reason=None):
        self.msg = msg or f"One of {arguments} must be passed to this method." + (reason or "")
        super(ArgumentMissingError, self).__init__(self.msg)


# ======= Payment =======

class NoPaymentMethodFoundError(Exception):
    def __init__(self, msg: str = None, reason=None):
        self.msg = msg or ("No eligible payment method found." + "" or reason)
        super(NoPaymentMethodFoundError, self).__init__(self.msg)


class AlreadyRemindedPaymentError(Exception):
    def __init__(self, payment_id: int):
        self.msg = f"A reminder has already been sent to the recipient of this transaction: {payment_id}."
        super(AlreadyRemindedPaymentError, self).__init__(self.msg)


class NoPendingPaymentToUpdateError(Exception):
    def __init__(self, payment_id: int, action: str):
        self.msg = f"There is no *pending* transaction with the specified id: {payment_id}, to be {action}ed."
        super(NoPendingPaymentToUpdateError, self).__init__(self.msg)


class NotEnoughBalanceError(Exception):
    def __init__(self, amount, target_user_id):
        self.msg = f"Failed to complete transaction of ${amount} to {target_user_id}.\n" \
                   f"There is not enough balance on the default payment method to complete the transaction.\n" \
                   f"hint: Use other payment methods like\n" \
                   f"send_money(amount, tr_note, target_user_id, funding_source_id=other_payment_id_here)\n" \
                   f"or transfer money to your default payment method.\n"
        super(NotEnoughBalanceError, self).__init__(self.msg)


class GeneralPaymentError(Exception):
    def __init__(self, msg):
        self.msg = f"Transaction failed. {msg}"
        super(GeneralPaymentError, self).__init__(self.msg)


__all__ = ["AuthenticationFailedError", "InvalidArgumentError", "InvalidHttpMethodError", "ArgumentMissingError",
           "JSONDecodeError", "ResourceNotFoundError", "HttpCodeError", "NoPaymentMethodFoundError",
           "AlreadyRemindedPaymentError", "NoPendingPaymentToUpdateError", "NotEnoughBalanceError",
           "GeneralPaymentError"
           ]
