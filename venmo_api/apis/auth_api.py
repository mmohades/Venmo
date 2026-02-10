from venmo_api.apis.api_client import ApiClient
from venmo_api.apis.api_util import ValidatedResponse, confirm, warn
from venmo_api.apis.exception import AuthenticationFailedError

# NOTE: ApiClient owns device-id now


class AuthenticationApi:
    """Auth API for logging in/out of your account.

    Args:
        api_client (ApiClient): Pre-initialized ApiClient that holds device-id. This
            instance will be logged in with the access token returned.
    """

    TWO_FACTOR_ERROR_CODE = 81109

    def __init__(self, api_client: ApiClient):
        self._api_client = api_client

    def login_with_credentials_cli(self, username: str, password: str) -> str:
        """Pass your username and password to get an access_token for using the API.

        Args:
            username (str): Phone, email or username
            password (str): Your account password to login

        Returns:
            str: access token generated for this session
        """
        # Give warnings to the user about device-id and token expiration
        warn(
            "IMPORTANT: Take a note of your device-id to avoid 2-factor-authentication for your next login."
        )
        print(f"device-id: {self.get_device_id()}")
        warn(
            "IMPORTANT: Your Access Token will NEVER expire, unless you logout manually (client.log_out(token)).\n"
            "Take a note of your token, so you don't have to login every time.\n"
        )
        response = self.authenticate_using_username_password(username, password)

        # if two-factor error
        if response.body.get("error"):
            access_token = self._two_factor_process_cli(response=response)
            self.trust_this_device()
        else:
            access_token = response.body["access_token"]

        confirm("Successfully logged in. Note your token and device-id")
        print(f"access_token: {access_token}\ndevice-id: {self.get_device_id()}")
        self._api_client.update_access_token(access_token)

        return access_token

    def authenticate_using_username_password(
        self, username: str, password: str
    ) -> ValidatedResponse:
        """Authenticate with username and password. Raises exception if either are incorrect.
        Check returned response:
            - if it has an error (response.body.error), 2-factor is needed
            - if no error, (response.body.access_token) gives you the access_token

        Args:
            username (str): Phone, email or username
            password (str): Your account password to login

        Returns:
            ValidatedResponse: validated response containing access token
        """
        body = {
            "phone_email_or_username": username,
            "client_id": "1",
            "password": password,
        }

        return self._api_client.call_api(
            resource_path="/oauth/access_token",
            body=body,
            method="POST",
            ok_error_codes=[self.TWO_FACTOR_ERROR_CODE],
        )

    @staticmethod
    def log_out(access_token: str) -> bool:
        """Revoke your access_token

        Args:
            access_token (str): token for session you want to log out of.

        Returns:
            bool: True or raises exception.
        """
        api_client = ApiClient(access_token=access_token)
        api_client.call_api(resource_path="/oauth/access_token", method="DELETE")
        confirm("Successfully logged out.")
        return True

    def _two_factor_process_cli(self, response: ValidatedResponse) -> str:
        """Get response from authenticate_with_username_password for a CLI two-factor process

        Args:
            response (ValidatedResponse): validated response

        Raises:
            AuthenticationFailedError

        Returns:
            str: access token generated for this session
        """
        otp_secret = response.headers.get("venmo-otp-secret")
        if not otp_secret:
            raise AuthenticationFailedError(
                "Failed to get the otp-secret for the 2-factor authentication process. "
                "(check your password)"
            )

        self.send_text_otp(otp_secret=otp_secret)
        user_otp = self._ask_user_for_otp_password()
        access_token = self.authenticate_using_otp(user_otp, otp_secret)
        self._api_client.update_access_token(access_token)

        return access_token

    def send_text_otp(self, otp_secret: str) -> ValidatedResponse:
        """Send one-time-password to user phone-number

        Args:
            otp_secret (str): the otp-secret from response_headers.venmo-otp-secret

        Raises:
            AuthenticationFailedError

        Returns:
            ValidatedResponse: validated response
        """
        response = self._api_client.call_api(
            resource_path="/account/two-factor/token",
            headers={"venmo-otp-secret": otp_secret},
            body={"via": "sms"},
            method="POST",
        )

        if response.status_code != 200:
            reason = None
            try:
                reason = response.body["error"]["message"]
            finally:
                raise AuthenticationFailedError(
                    f"Failed to send the One-Time-Password to"
                    f" your phone number because: {reason}"
                )

        return response

    def authenticate_using_otp(self, user_otp: str, otp_secret: str) -> str:
        """Login using one-time-password, for 2-factor process

        Args:
            user_otp (str): otp user received on their phone
            otp_secret (str): otp_secret obtained from 2-factor process

        Returns:
            str: _description_
        """
        headers = {"venmo-otp": user_otp, "venmo-otp-secret": otp_secret}
        response = self._api_client.call_api(
            resource_path="/oauth/access_token",
            headers=headers,
            params={"client_id": 1},
            method="POST",
        )
        return response.body["access_token"]

    def trust_this_device(self):
        """
        Add current device_id to the trusted devices on Venmo
        """
        self._api_client.call_api(resource_path="/users/devices", method="POST")
        confirm("Successfully added your device id to the list of the trusted devices.")
        print(
            f"Use the same device-id: {self.get_device_id()} next time to avoid 2-factor-auth process."
        )

    def get_device_id(self):
        return self._api_client.device_id

    @staticmethod
    def _ask_user_for_otp_password():
        otp = ""
        while len(otp) < 6 or not otp.isdigit():
            otp = input(
                "Enter OTP that you received on your phone from Venmo: (It must be 6 digits)\n"
            )

        return otp
