from api_client import ApiClient
from apis.user_api import UserApi


class VenmoApi(object):

    def __init__(self, access_token):
        super().__init__()
        self._access_token = access_token
        self._api_client = ApiClient(access_token=access_token)
        self._user_api = UserApi(self._api_client)

    def user(self):
        return self._user_api
