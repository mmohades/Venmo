from datetime import datetime
from random import randint, choice
from string import ascii_uppercase
from enum import Enum
from typing import Dict


def string_to_timestamp(utc):
    """
    Convert UTC string format by Venmo, to timestamp
    :param utc: String, Format "2019-02-07T18:04:18"
    :return: int, timestamp
    """
    if not utc:
        return

    _date = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S')

    return int(_date.timestamp())


def get_phone_model_from_json(app_json):
    app = {1: "iPhone", 4: "Android"}
    _id = app_json['id']

    return app.get(int(_id)) or "undefined"


def random_device_id():

    BASE_DEVICE_ID = "88884260-05O3-8U81-58I1-2WA76F357GR9"

    result = []
    for char in BASE_DEVICE_ID:

        if char.isdigit():
            result.append(str(randint(0, 9)))
        elif char == '-':
            result.append('-')
        else:
            result.append(choice(ascii_uppercase))

    return "".join(result)


def deserialize(response: Dict, data_type):
    """Extract one or a list of Objects from the api_client structured response.
    :param response: <Dict>
    :param data_type: <Generic>
    :return:
    """

    body = response.get('body')

    if not body:
        raise Exception("Can't process an empty response body.")

    data = body.get('data')

    # Return a list of <class>
    if isinstance(data, list):
        return __get_objs_from_json_list(json_list=data, data_type=data_type)

    return data_type.from_json(json=data)


def wrap_callback(callback, data_type):
    """
    :param callback: <function> Function that was provided by the user
    :param data_type: <class> It can be either User or Transaction
    :return wrapped_callback: <function> or <NoneType> The user callback wrapped for json parsing.
    """
    if not callback:
        return None

    def wrapper(response):

        if not data_type:
            return callback(True)

        deserialized_data = deserialize(response=response, data_type=data_type)
        return callback(deserialized_data)

    return wrapper


def __get_objs_from_json_list(json_list, data_type):
    """Process JSON for User/Transaction
    :param json_list: <list> a list of objs
    :param data_type: <class> Either User/Transaction
    :return: <list> a list of <User>
    """
    return [data_type.from_json(obj) for obj in json_list]


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
    print(Colors.WARNING + message + Colors.ENDC)


def confirm(message):
    print(Colors.OKBLUE + message + Colors.ENDC)
