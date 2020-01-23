from api_client import ApiClient
from apis.user_api import UserApi
from apis.auth_api import AuthenticationApi


class VenmoApi(object):

    def __init__(self, access_token: str):
        """

        :param access_token: <str> Get access token to work with the API.
        """
        super().__init__()
        self.__access_token = access_token
        self.__api_client = ApiClient(access_token=access_token)
        self.__user_api = UserApi(self.__api_client)

    def user(self):
        return self.__user_api

    @classmethod
    def get_auth_token(cls, username: str, password: str, device_id: str = None):

        auth_api = AuthenticationApi(api_client=ApiClient(), device_id=device_id)
        return auth_api.login_using_credentials(username=username, password=password)

    @classmethod
    def log_out(cls, access_token):
        return AuthenticationApi.log_out(access_token=access_token)
