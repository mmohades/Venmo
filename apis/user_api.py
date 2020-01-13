
"""
This class will be for the user related routes
They need to use the api_client for making the requests. Routes will be defined here tho.
Routes and formatting will be here.
"""


class UserApi(object):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client
