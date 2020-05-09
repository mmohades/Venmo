from venmo_api import random_device_id, warn, confirm
from venmo_api import AuthenticationFailedError
from venmo_api import ApiClient


class AuthenticationApi(object):
    def __init__(self, api_client: ApiClient, device_id: str = None):
        super().__init__()

        self.__device_id = device_id or random_device_id()
        self.__api_client = api_client

    def login_using_credentials(self, username: str, password: str) -> str:
        """
        Pass your username and password to get an access_token for using the API.
        :param username: <str> Phone, email or username
        :param password: <str> Your account password to login
        :return:
        """

        # Give some warnings to the user for their future benefit
        warn("IMPORTANT: Take a note of your device id to avoid 2-Factor-Authentication for your next login.")
        print(f"device-id: {self.__device_id}")
        warn("IMPORTANT: Your Access Token will never expire, unless you logout using it."
             " Take a note of it for your future use or even for logging out, you will need it.\n")

        header_params = {'device-id': self.__device_id,
                         'Content-Type': 'application/json',
                         'Host': 'api.venmo.com'
                         }

        body = {"phone_email_or_username": username,
                "client_id": "1",
                "password": password
                }
        resource_path = '/oauth/access_token'

        response = self.__api_client.call_api(resource_path=resource_path, header_params=header_params,
                                              body=body, method='POST', ok_error_codes=[81109])

        if response.get('body').get('error'):
            access_token = self.__two_factor_process(response=response)
            self.__trust_this_device()
        else:
            access_token = response['body']['access_token']

        confirm("Successfully logged in.")
        print(f"access_token: {access_token}")

        return access_token

    def __two_factor_process(self, response):

        otp_secret = response['headers'].get('venmo-otp-secret')
        if not otp_secret:
            raise AuthenticationFailedError("Failed to get the otp-secret for the 2-factor authentication process. "
                                            "(check your password)")

        self.__send_text_otp(otp_secret=otp_secret)
        user_otp = self.__ask_user_for_otp_password()

        access_token = self.__login_using_otp(user_otp, otp_secret)
        self.__api_client.update_access_token(access_token=access_token)

        return access_token

    def __send_text_otp(self, otp_secret):

        header_params = {'device-id': self.__device_id,
                         'Content-Type': 'application/json',
                         'venmo-otp-secret': otp_secret
                         }
        body = {"via": "sms"}
        resource_path = '/account/two-factor/token'

        response = self.__api_client.call_api(resource_path=resource_path, header_params=header_params,
                                              body=body, method='POST', ok_error_codes=[81109])

        if response['status_code'] != 200:
            reason = None
            try:
                reason = response['body']['error']['message']
            finally:
                raise AuthenticationFailedError(f"Failed to send the One-Time-Password to"
                                                f" your phone number because: {reason}")

        return response

    @staticmethod
    def __ask_user_for_otp_password():

        otp = ""
        while len(otp) < 6 or not otp.isdigit():
            otp = input("Enter OTP that you received on your phone from Venmo: (It must be 6 digits)\n")

        return otp

    def __login_using_otp(self, user_otp, otp_secret):

        header_params = {'device-id': self.__device_id,
                         'venmo-otp': user_otp,
                         'venmo-otp-secret': otp_secret
                         }
        params = {'client_id': 1}
        resource_path = '/oauth/access_token'

        response = self.__api_client.call_api(resource_path=resource_path, header_params=header_params,
                                              params=params,
                                              method='POST')

        return response['body']['access_token']

    def __trust_this_device(self):

        header_params = {'device-id': self.__device_id}
        resource_path = '/users/devices'

        self.__api_client.call_api(resource_path=resource_path,
                                   header_params=header_params,
                                   method='POST')

        confirm(f"Successfully added your device id to the list of the trusted devices.")
        print(f"Use the same device-id  {self.__device_id}  next time to avoid 2-factor-auth process.")

    @staticmethod
    def log_out(access_token: str) -> bool:
        """
        Revoke your access_token
        :param access_token: <str>
        :return:
        """

        resource_path = '/oauth/access_token'
        api_client = ApiClient(access_token=access_token)

        api_client.call_api(resource_path=resource_path,
                            method='DELETE')

        confirm(f"Successfully logged out.")
        return True
