from venmo_api import User
from venmo_api import Transaction
from venmo_api import InvalidArgumentError, ArgumentMissingError
from venmo_api import deserialize, wrap_callback
from threading import Thread
from typing import List, Union


class UserApi(object):
    def __init__(self, api_client):
        super().__init__()
        self.__api_client = api_client

    def search_for_users(self, query: str, callback=None,
                         page: int = 1, count: int = 50) -> Union[List[User], Thread]:
        """
        :param query: <str>
        :param callback: <function>
        :param count: <int>
        :param page: <int>
        :return users_list: <list> A list of <User> objects or empty
        """

        resource_path = '/users'
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=User)

        offset_limit_params = self.__prepare_offset_limit_params(page_number=page,
                                                                 max_number_per_page=50,
                                                                 max_offset=9900,
                                                                 count=count)
        params = {'query': query}
        params.update(offset_limit_params)

        response = self.__api_client.call_api(resource_path=resource_path, params=params,
                                              method='GET', callback=wrapped_callback)
        # return the Thread
        if callback:
            return response

        return deserialize(response=response, data_type=User)

    def get_profile(self, user_id: str, callback=None) -> Union[User, Thread, None]:
        """
        :param user_id: <str>, example: '2859950549165568970'
        :param callback: <function>
        :return user: <User> <Thread> <NoneType>
        """

        # Prepare the request
        resource_path = f'/users/{user_id}'
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=User)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET',
                                              callback=wrapped_callback)
        # Return the thread
        if callback:
            return response

        return deserialize(response=response, data_type=User)

    def get_user_friends_list(self, user: User = None,
                              user_id: str = None,
                              callback=None,
                              page: int = 1,
                              count: int = 1337) -> Union[User, Thread, None]:
        """

        :return users_list: <list> A list of <User> objects or empty
        """
        user_id = user_id or user.id

        if not user_id:
            raise ArgumentMissingError(arguments=("user", "user_id"))
        params = self.__prepare_offset_limit_params(page_number=page,
                                                    max_number_per_page=1337,
                                                    max_offset=9999999999999999999,
                                                    count=count)

        # Prepare the request
        resource_path = f'/users/{user_id}/friends'
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=User)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET', params=params,
                                              callback=wrapped_callback)
        # Return the Thread
        if callback:
            return response

        return deserialize(response=response, data_type=User)

    def get_user_transactions(self, user: User = None, user_id: str = None,
                              callback=None,
                              page: int = 1,
                              count: int = 50) -> Union[Transaction, Thread, None]:

        user_id = user_id or user.id

        if not user_id:
            raise ArgumentMissingError(arguments=("user", "user_id"))
        params = self.__prepare_offset_limit_params(page_number=page,
                                                    max_number_per_page=50,
                                                    max_offset=9900,
                                                    count=count)

        # Prepare the request
        resource_path = f'/stories/target-or-actor/{user_id}'

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=Transaction)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET', params=params,
                                              callback=wrapped_callback)
        # Return the Thread
        if callback:
            return response

        return deserialize(response=response, data_type=Transaction)

    def get_transaction_between_two_users(self, user_one: User = None,
                                          user_id_one: str = None,
                                          user_two: User = None,
                                          user_id_two: str = None,
                                          callback=None,
                                          page: int = 1,
                                          count: int = 50) -> Union[Transaction, Thread, None]:

        user_id_one = user_id_one or user_one.id
        user_id_two = user_id_two or user_two.id

        if not user_id_one or not user_id_two:
            raise ArgumentMissingError(arguments=("user", "user_id"),
                                       reason="User or user_id must be provided for both users.")

        params = self.__prepare_offset_limit_params(page_number=page,
                                                    max_number_per_page=50,
                                                    max_offset=9900,
                                                    count=count)

        # Prepare the request
        resource_path = f'/stories/target-or-actor/{user_id_one}/target-or-actor/{user_id_two}'

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=Transaction)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET', params=params,
                                              callback=wrapped_callback)
        # Return the Thread
        if callback:
            return response

        return deserialize(response=response, data_type=Transaction)

    @staticmethod
    def __prepare_offset_limit_params(page_number, max_number_per_page, max_offset, count):
        """Get the offset for going to that page."""
        max_page = max_offset//max_number_per_page + 1
        if page_number == 0 or page_number > max_page:
            raise InvalidArgumentError(argument_name="'page number'",
                                       reason=f"Page number must be an int bigger than 1 smaller than {max_page}.")

        offset = (page_number - 1) * max_number_per_page

        return {'offset': offset, 'limit': count}
