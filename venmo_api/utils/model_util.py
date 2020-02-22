from datetime import datetime
from random import randint, choice
from string import ascii_uppercase


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
    """
    extract the phone model from app_info json.
    :param app_json:
    :return:
    """
    app = {1: "iPhone", 4: "Android"}
    _id = app_json['id']

    return app.get(int(_id)) or "undefined"


def random_device_id():
    """
    Generate a random device id that can be used for logging in.
    :return:
    """
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
