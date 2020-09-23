from enum import Enum
from typing import Dict, List
from venmo_api import ArgumentMissingError, User


def validate_access_token(access_token):
    """
    Validate the access_token
    :param access_token:
    :return:
    """
    if not access_token:
        return

    if access_token[:6] != 'Bearer':
        return f"Bearer {access_token}"

    return access_token


def deserialize(response: Dict, data_type, nested_response: List[str] = None):
    """Extract one or a list of Objects from the api_client structured response.
    :param response: <Dict>
    :param data_type: <Generic>
    :param nested_response: <List[str]> Optional. Loop through the body
    :return:
    """

    body = response.get('body')
    if not body:
        raise Exception("Can't  get an empty response body.")

    data = body.get('data')
    nested_response = nested_response or []
    for nested in nested_response:
        temp = data.get(nested)
        if not temp:
            raise ValueError(f"Couldn't find {nested} in the {data}.")
        data = temp

    # Return a list of <class> data_type
    if isinstance(data, list):
        return __get_objs_from_json_list(json_list=data, data_type=data_type)

    return data_type.from_json(json=data)


def wrap_callback(callback, data_type, nested_response: List[str] = None):
    """
    :param callback: <function> Function that was provided by the user
    :param data_type: <class> It can be either User or Transaction
    :param nested_response: <List[str]> Optional. Loop through the body
    :return wrapped_callback: <function> or <NoneType> The user callback wrapped for json parsing.
    """
    if not callback:
        return None

    def wrapper(response):

        if not data_type:
            return callback(True)

        deserialized_data = deserialize(response=response, data_type=data_type, nested_response=nested_response)
        return callback(deserialized_data)

    return wrapper


def __get_objs_from_json_list(json_list, data_type):
    """Process JSON for User/Transaction
    :param json_list: <list> a list of objs
    :param data_type: <class> Either User/Transaction
    :return: <list> a list of <User>
    """
    result = []
    for obj in json_list:
        data_obj = data_type.from_json(obj)
        if not data_obj:
            continue
        result.append(data_obj)

    return result


class Colors(Enum):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def warn(message):
    """
    print message in Red Color
    :param message:
    :return:
    """
    print(Colors.WARNING.value + message + Colors.ENDC.value)


def confirm(message):
    """
    print message in Blue Color
    :param message:
    :return:
    """
    print(Colors.OKBLUE.value + message + Colors.ENDC.value)


def get_user_id(user, user_id):
    """
    Checks at least one user_id exists and returns it
    :param user_id:
    :param user:
    :return user_id:
    """
    if not user and not user_id:
        raise ArgumentMissingError(arguments=('target_user_id', 'target_user'))

    if not user_id:
        if type(user) != User:
            raise ArgumentMissingError(f"Expected {User} for target_user, but received {type(user)}")

        user_id = user.id

    return user_id
