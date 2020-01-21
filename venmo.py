from api_client import ApiClient
from apis.user_api import UserApi


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
