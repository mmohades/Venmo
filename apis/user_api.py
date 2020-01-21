from typing import List, Optional, Union
from models.user import User

"""
This class will be for the user related routes
They need to use the api_client for making the requests. Routes will be defined here tho.
Routes and formatting will be here.
"""


class UserApi(object):
    def __init__(self, api_client):
        super().__init__()
        self.api_client = api_client

    def search_for_users(self, query: str, callback=None,
                         count: int = 50, page: int = 1) -> List[User]:
        """
        :param query: <str>
        :param callback: <function>
        :param count: <int>
        :param page: <int>
        :return users_list: <list> A list of <User> objects or empty
        """

        resource_path = '/users'
        wrapped_callback = self._wrap_callback(callback=callback,
                                               data_type=User)
        params = {"query": query}
        response = self.api_client.call_api(resource_path=resource_path, params=params,
                                            method='GET', callback=wrapped_callback)

        if callback:
            return []

        return self.__deserialize(response=response, data_type=User)

    def get_user_profile(self, user_id: str, callback=None) -> Union[User, None]:
        """
        :param user_id: <str>, example: '35850181'
        :param callback: <function>
        :return user: <User>
        """
        # Prepare the request
        resource_path = f'/users/{user_id}'
        wrapped_callback = self._wrap_callback(callback=callback,
                                               data_type=User)
        # Make the request
        response = self.api_client.call_api(resource_path=resource_path,
                                            method='GET', callback=wrapped_callback)
        # Return or process the response
        if callback:
            return

        return self.__deserialize(response=response, data_type=User)

    def get_user_friends_list(self):
        """

        :return users_list: <list> A list of <User> objects or empty
        """
        pass

    def get_user_transactions(self):
        pass

    def get_transaction_between_two_users(self):
        pass

    def _wrap_callback(self, callback, data_type):
        """
        :param callback: <function> Function that was provided by the user
        :param data_type: <class> It can be either User or Transaction
        :return wrapped_callback: <function> or <NoneType> The user callback wrapped for json parsing.
        """
        if not callback:
            return None

        def wrapper(response):

            deserialized_data = self.__deserialize(response=response, data_type=data_type)
            return callback(deserialized_data)

        return wrapper


    def __deserialize(self, response, data_type):
        """Extract one or a list of users from the api_client requested response.
        :param response:
        :param data_type:
        :return:
        """
        body = response.get('body')

        if not body:
            raise Exception("Can't process an empty response body.")

        data = body.get('data')

        # Return a list of users (Friends list, etc)
        if isinstance(data, list):
            return self.__get_objs_from_json_list(json_list=data, data_type=data_type)

        return data_type.from_json(json=data)


    def __get_objs_from_json_list(self, json_list, data_type):
        """Process JSON for User/Transaction
        :param json_list: <list> a list of objs
        :param data_type: <class> Either User/Transaction
        :return: <list> a list of <User>
        """

        return [data_type.from_json(obj) for obj in json_list]
