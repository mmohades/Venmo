import re
from venmo_api import User
from venmo_api import Transaction
from venmo_api import InvalidArgumentError
from venmo_api import deserialize, wrap_callback, get_user_id
from typing import List, Union


class UserApi(object):
    def __init__(self, api_client):
        super().__init__()
        self.__api_client = api_client
        self.__profile = None

    def get_my_profile(self, callback=None, force_update=False) -> Union[User, None]:
        """
        Get my profile info and return as a <User>
        :return my_profile: <User>
        """
        if self.__profile and not force_update:
            return self.__profile

        # Prepare the request
        resource_path = '/account'
        nested_response = ['user']
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=User,
                                         nested_response=nested_response)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET',
                                              callback=wrapped_callback)
        # Return None if threaded
        if callback:
            return

        self.__profile = deserialize(response=response, data_type=User, nested_response=nested_response)
        return self.__profile

    def search_for_users(self, query: str, callback=None,
                         page: int = 1, count: int = 50) -> Union[List[User], None]:
        """
        search for [query] in users
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
        # Return None if threaded
        if callback:
            return

        return deserialize(response=response, data_type=User)

    def get_user(self, user_id: str, callback=None) -> Union[User, None]:
        """
        Get the user profile with [user_id]
        :param user_id: <str>, example: '2859950549165568970'
        :param callback: <function>
        :return user: <User> <NoneType>
        """

        # Prepare the request
        resource_path = f'/users/{user_id}'
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=User)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET',
                                              callback=wrapped_callback)
        # Return None if threaded
        if callback:
            return

        return deserialize(response=response, data_type=User)

    def get_user_friends_list(self, user_id: str = None,
                              user: User = None,
                              callback=None,
                              page: int = 1,
                              count: int = 1337) -> Union[User, None]:
        """
        Get ([user_id]'s or [user]'s) friends list as a list of <User>s
        :return users_list: <list> A list of <User> objects or empty
        """
        user_id = get_user_id(user, user_id)
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
        # Return None if threaded
        if callback:
            return

        return deserialize(response=response, data_type=User)

    def get_user_transactions(self, user_id: str = None, user: User = None,
                              callback=None,
                              count: int = 50,
                              before_id=None) -> Union[Transaction, None]:
        """
        Get ([user_id]'s or [user]'s) transactions visible to yourself as a list of <Transaction>s
        :param user_id:
        :param user:
        :param callback:
        :param count:
        :param before_id:
        :return:
        """
        user_id = get_user_id(user, user_id)

        params = {'limit': count}
        if before_id:
            params['before_id'] = before_id

        # Prepare the request
        resource_path = f'/stories/target-or-actor/{user_id}'

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=Transaction)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET', params=params,
                                              callback=wrapped_callback)
        # Return None if threaded
        if callback:
            return

        return deserialize(response=response, data_type=Transaction)

    def get_transaction_between_two_users(self, user_id_one: str = None,
                                          user_id_two: str = None,
                                          user_one: User = None,
                                          user_two: User = None,
                                          callback=None,
                                          count: int = 50,
                                          before_id=None) -> Union[Transaction, None]:
        """
        Get the transactions between two users. Note that user_one must be the owner of the access token.
        Otherwise it raises an unauthorized error.
        :param user_id_one:
        :param user_id_two:
        :param user_one:
        :param user_two:
        :param callback:
        :param count:
        :param before_id:
        :return:
        """
        user_id_one = get_user_id(user_one, user_id_one)
        user_id_two = get_user_id(user_two, user_id_two)

        params = {'limit': count}
        if before_id:
            params['before_id'] = before_id

        # Prepare the request
        resource_path = f'/stories/target-or-actor/{user_id_one}/target-or-actor/{user_id_two}'

        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=Transaction)
        # Make the request
        response = self.__api_client.call_api(resource_path=resource_path,
                                              method='GET', params=params,
                                              callback=wrapped_callback)
        # Return None if threaded
        if callback:
            return

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

    @staticmethod
    def __last_transaction_id(body):
        pagination = body.get("pagination")
        if not pagination:
            return

        next_link = pagination.get("next")
        pattern = r'before_id=(\d*)'
        if not next_link:
            return

        match = re.search(pattern, next_link)
        if not match.groups():
            return

        return {"before_id": match.groups()[0]}
