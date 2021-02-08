from datetime import datetime
from random import randint, choice
from string import ascii_uppercase


def string_to_timestamp(utc):
    """
    Convert UTC string format by Venmo, to timestamp
    :param utc: String, Format "2019-02-07T18:04:18" or "2019-02-07T18:04:18.474000"
    :return: int, timestamp
    """
    if not utc:
        return
    try:
        _date = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S')
    # This except was added for comments (on transactions) - they display the date_created down to the microsecond
    except ValueError:
        _date = datetime.strptime(utc, '%Y-%m-%dT%H:%M:%S.%f')
    return int(_date.timestamp())


def get_phone_model_from_json(app_json):
    """
    extract the phone model from app_info json.
    :param app_json:
    :return:
    """
    app = {1: "iPhone", 4: "Android", 0: "Other"}
    _id = 0
    if app_json:
        _id = app_json['id']

    return app.get(int(_id))


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
