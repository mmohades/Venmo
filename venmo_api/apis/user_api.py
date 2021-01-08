from venmo_api import User, Page, Transaction, deserialize, wrap_callback, get_user_id
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
                         offset: int = 0, limit: int = 50, username=False) -> Union[List[User], None]:
        """
        search for [query] in users
        :param query:
        :param callback:
        :param offset:
        :param limit:
        :param username: default: False; Pass True if search is by username
        :return users_list: <list> A list of <User> objects or empty
        """

        resource_path = '/users'
        wrapped_callback = wrap_callback(callback=callback,
                                         data_type=User)

        params = {'query': query, 'limit': limit, 'offset': offset}
        # update params for querying by username
        if username or '@' in query:
            params.update({'query': query.replace('@', ''), 'type': 'username'})

        response = self.__api_client.call_api(resource_path=resource_path, params=params,
                                              method='GET', callback=wrapped_callback)
        # Return None if threaded
        if callback:
            return

        return deserialize(response=response,
                           data_type=User).set_method(method=self.search_for_users,
                                                      kwargs={"query": query, "limit": limit},
                                                      current_offset=offset
                                                      )


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

    def get_user_by_username(self, username: str) -> Union[User, None]:
        """
        Get the user profile with [username]
        :param username:
        :return user: <User> <NoneType>
        """
        users = self.search_for_users(query=username, username=True)
        for user in users:
            if user.username == username:
                return user

        # username not found
        return None

    def get_user_friends_list(self, user_id: str = None,
                              user: User = None,
                              callback=None,
                              offset: int = 0,
                              limit: int = 3337) -> Union[Page, None]:
        """
        Get ([user_id]'s or [user]'s) friends list as a list of <User>s
        :return users_list: <list> A list of <User> objects or empty
        """
        user_id = get_user_id(user, user_id)
        params = {"limit": limit, "offset": offset}

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

        return deserialize(
            response=response,
            data_type=User).set_method(method=self.get_user_friends_list,
                                       kwargs={"user_id": user_id, "limit": limit},
                                       current_offset=offset
                                       )

    def get_user_transactions(self, user_id: str = None, user: User = None,
                              callback=None,
                              limit: int = 50,
                              before_id=None) -> Union[Page, None]:
        """
        Get ([user_id]'s or [user]'s) transactions visible to yourself as a list of <Transaction>s
        :param user_id:
        :param user:
        :param callback:
        :param limit:
        :param before_id:
        :return:
        """
        user_id = get_user_id(user, user_id)

        params = {'limit': limit}
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

        return deserialize(response=response,
                           data_type=Transaction).set_method(method=self.get_user_transactions,
                                                             kwargs={"user_id": user_id})

    def get_transaction_between_two_users(self, user_id_one: str = None,
                                          user_id_two: str = None,
                                          user_one: User = None,
                                          user_two: User = None,
                                          callback=None,
                                          limit: int = 50,
                                          before_id=None) -> Union[Page, None]:
        """
        Get the transactions between two users. Note that user_one must be the owner of the access token.
        Otherwise it raises an unauthorized error.
        :param user_id_one:
        :param user_id_two:
        :param user_one:
        :param user_two:
        :param callback:
        :param limit:
        :param before_id:
        :return:
        """
        user_id_one = get_user_id(user_one, user_id_one)
        user_id_two = get_user_id(user_two, user_id_two)

        params = {'limit': limit}
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

        return deserialize(response=response,
                           data_type=Transaction).set_method(method=self.get_transaction_between_two_users,
                                                             kwargs={"user_id_one": user_id_one,
                                                                             "user_id_two": user_id_two})
