from datetime import datetime, timezone
from random import randint, choice
from string import ascii_uppercase


def string_to_timestamp(utc):
    """
    Convert UTC string format by Venmo, to timestamp
    :param utc: String, Example "2019-02-07T18:04:18"
    :return: int, timestamp
    """
    if not utc:
        return

    year = int(utc[:4])
    month = int(utc[5:7])
    day = int(utc[8:10])
    hour = int(utc[11:13])
    minute = int(utc[14:16])
    second = int(utc[17:19])

    _date = datetime(year=year,
                     month=month,
                     day=day or 1,
                     hour=hour or 12,
                     minute=minute or 0,
                     second=second or 0,
                     tzinfo=timezone.utc)

    return int(_date.timestamp())


def get_phone_model_from_json(app_json):
    app = {1: "iPhone", 4: "Android"}
    _id = app_json['id']

    return app.get(int(_id)) or "Not a phone app"


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

class Colors:
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
