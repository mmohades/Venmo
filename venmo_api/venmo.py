from venmo_api import ApiClient, UserApi, PaymentApi, AuthenticationApi, validate_access_token
from typing import Tuple


class Client(object):

    def __init__(self, access_token: str):
        """
        VenmoAPI Client
        :param access_token: <str> Need access_token to work with the API.
        """
        super().__init__()
        self.__access_token = validate_access_token(access_token=access_token)
        self.__api_client = ApiClient(access_token=access_token)
        self.user = UserApi(self.__api_client)
        self.__profile = self.user.get_my_profile()
        self.payment = PaymentApi(profile=self.__profile,
                                  api_client=self.__api_client)

    def my_profile(self, force_update=False):
        """
        Get your profile info. It can be cached from the prev time.
        :return:
        """
        if force_update:
            self.__profile = self.user.get_my_profile(force_update=force_update)

        return self.__profile

    @staticmethod
    def get_access_token(username: str, password: str, device_id: str = None, get_2fa_code_from_file_path: str = None) -> Tuple[str, str]:
        """
        Log in using your credentials and get an access_token to use in the API
        :param username: <str> Can be username, phone number (without +1) or email address.
        :param password: <str> Account's password
        :param device_id: <str> [optional] A valid device-id.
        :param get_2fa_code_from_file_path: <str> [optional] Path to 2fa code txt file

        :return: (<str> access_token, <str> device_id)
        """
        authn_api = AuthenticationApi(api_client=ApiClient(), device_id=device_id)
        return authn_api.login_with_credentials_cli(username=username, password=password, get_2fa_code_from_file_path=get_2fa_code_from_file_path)

    @staticmethod
    def log_out(access_token) -> bool:
        """
        Revoke your access_token. Log out, in other words.
        :param access_token:
        :return: <bool>
        """
        access_token = validate_access_token(access_token=access_token)
        return AuthenticationApi.log_out(access_token=access_token)
