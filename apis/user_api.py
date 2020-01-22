from typing import List, Union
from models.user import User
from models.transaction import Transaction
from models.exception import InvalidArgumentError, ArgumentMissingError

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
                         page: int = 1, count: int = 50) -> List[User]:
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

        offset = self.get_offset_by_page(page_number=page,
                                         max_number_per_page=50,
                                         max_offset=9900)

        params = {'query': query, 'offset': offset, 'limit': count}
        response = self.api_client.call_api(resource_path=resource_path, params=params,
                                            method='GET', callback=wrapped_callback)

        if callback:
            return []

        return self.__deserialize(response=response, data_type=User)

    def get_user_profile(self, user_id: str, callback=None) -> Union[User, None]:
        """
        :param user_id: <str>, example: '2859950549165568970'
        :param callback: <function>
        :return user: <User>
        """

        # Prepare the request
        resource_path = f'/users/{user_id}'
        wrapped_callback = self._wrap_callback(callback=callback,
                                               data_type=User)
        # Make the request
        response = self.api_client.call_api(resource_path=resource_path,
                                            method='GET',
                                            callback=wrapped_callback)
        # Return or process the response
        if callback:
            return

        return self.__deserialize(response=response, data_type=User)

    def get_user_friends_list(self, user: User = None, user_id: str = None,
                              callback=None,
                              page: int = 1, count: int = 1337):
        """

        :return users_list: <list> A list of <User> objects or empty
        """
        user_id = user_id or user.id

        if not user_id:
            raise ArgumentMissingError(arguments=("user", "user_id"))
        offset = self.get_offset_by_page(page_number=page,
                                         max_number_per_page=1337,
                                         max_offset=9999999999999999999)

        params = {'offset': offset, 'limit': count}

        # Prepare the request
        resource_path = f'/users/{user_id}/friends'
        wrapped_callback = self._wrap_callback(callback=callback,
                                               data_type=User)
        # Make the request
        response = self.api_client.call_api(resource_path=resource_path,
                                            method='GET', params=params,
                                            callback=wrapped_callback)
        # Return or process the response
        if callback:
            return

        return self.__deserialize(response=response, data_type=User)

    def get_user_transactions(self, user: User = None, user_id: str = None,
                              callback=None,
                              page: int = 1, count: int = 50):

        user_id = user_id or user.id

        if not user_id:
            raise ArgumentMissingError(arguments=("user", "user_id"))
        offset = self.get_offset_by_page(page_number=page,
                                         max_number_per_page=50,
                                         max_offset=9900)

        params = {'offset': offset, 'limit': count}

        # Prepare the request
        resource_path = f'/stories/target-or-actor/{user_id}'

        wrapped_callback = self._wrap_callback(callback=callback,
                                               data_type=Transaction)
        # Make the request
        response = self.api_client.call_api(resource_path=resource_path,
                                            method='GET', params=params,
                                            callback=wrapped_callback)
        # Return or process the response
        if callback:
            return

        return self.__deserialize(response=response, data_type=Transaction)

    def get_transaction_between_two_users(self, user_one: User = None, user_id_one: str = None,
                                          user_two: User = None, user_id_two: str = None,
                                          callback=None,
                                          page: int = 1, count: int = 50):

        user_id_one = user_id_one or user_one.id
        user_id_two = user_id_two or user_two.id

        if not user_id_one or not user_id_two:
            raise ArgumentMissingError(arguments=("user", "user_id"),
                                       reason="User or user_id must be provided for both users.")

        offset = self.get_offset_by_page(page_number=page,
                                         max_number_per_page=50,
                                         max_offset=9900)

        params = {'offset': offset, 'limit': count}

        # Prepare the request
        resource_path = f'/stories/target-or-actor/{user_id_one}/target-or-actor/{user_id_two}'

        wrapped_callback = self._wrap_callback(callback=callback,
                                               data_type=Transaction)
        # Make the request
        response = self.api_client.call_api(resource_path=resource_path,
                                            method='GET', params=params,
                                            callback=wrapped_callback)
        # Return or process the response
        if callback:
            return

        return self.__deserialize(response=response, data_type=Transaction)

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

    def get_offset_by_page(self, page_number, max_number_per_page, max_offset):
        """Get the offset for going to that page."""
        max_page = max_offset//max_number_per_page + 1
        if page_number == 0 or page_number > max_page:
            raise InvalidArgumentError(argument_name="'page number'",
                                       reason=f"Page number must be an int bigger than 1 smaller than {max_page}.")

        return (page_number - 1) * max_number_per_page
