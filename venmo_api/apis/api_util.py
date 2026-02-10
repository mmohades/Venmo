from dataclasses import dataclass
from enum import Enum
from typing import Any

from pydantic import BaseModel
from requests.structures import CaseInsensitiveDict

from venmo_api.models.page import Page


@dataclass(frozen=True, slots=True)
class ValidatedResponse:
    status_code: int
    headers: CaseInsensitiveDict
    body: dict


def deserialize(
    response: ValidatedResponse,
    data_type: type[BaseModel | Any],
    nested_response: list[str] | None = None,
) -> Any | Page[Any]:
    """Extract one or a list of Objects from the api_client structured response.

    Args:
        response (ValidatedResponse): validated response.
        data_type (type[BaseModel  |  Any]): if data of interest is a json object,
            should be a pydantic BaseModel subclass. Otherwise can be a primitive class.
        nested_response (list[str] | None, optional): _description_. Defaults to None.

    Returns:
        Any | Page[Any]: a single <Object> or a <Page> of objects (Objects can be
            User/Transaction/Payment/PaymentMethod)
    """
    body = response.body
    if not body:
        raise Exception("Can't get an empty response body.")

    data = body.get("data")
    nested_response = nested_response or []
    for nested in nested_response:
        temp = data.get(nested)
        if not temp:
            raise ValueError(f"Couldn't find {nested} in the {data}.")
        data = temp

    # Return a list of <class> data_type
    if isinstance(data, list):
        return __get_objs_from_json_list(json_list=data, data_type=data_type)

    if issubclass(data_type, BaseModel):
        return data_type.model_validate(data)
    else:  # probably a primitive
        return data_type(data)


def __get_objs_from_json_list(
    json_list: list[Any], data_type: type[BaseModel | Any]
) -> Page[Any]:
    """Process response JSON for a data list.

    Args:
        json_list (list[Any]): a list of objs
        data_type (type[BaseModel  |  Any]): User/Transaction/Payment/PaymentMethod

    Returns:
        Page[Any]: list subclass container that can get its own next page.
    """
    result = Page()
    for elem in json_list:
        if issubclass(data_type, BaseModel):
            result.append(data_type.model_validate(elem))
        else:  # probably a primitive
            result.append(data_type(elem))

    return result


class Colors(Enum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def warn(message):
    """
    print message in Red Color
    """
    print(Colors.WARNING.value + message + Colors.ENDC.value)


def confirm(message):
    """
    print message in Blue Color
    """
    print(Colors.OKBLUE.value + message + Colors.ENDC.value)
