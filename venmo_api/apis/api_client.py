import os
import uuid
from json import JSONDecodeError
from random import getrandbits

import orjson
import requests

from venmo_api import PROJECT_ROOT
from venmo_api.apis.api_util import ValidatedResponse
from venmo_api.apis.exception import (
    HttpCodeError,
    InvalidHttpMethodError,
    ResourceNotFoundError,
)
from venmo_api.apis.logging_session import LoggingSession


def random_device_id() -> str:
    """
    Generate a random device id that can be used for logging in.
    NOTE: As of late 2025, they seem to have tightened security around device-ids, so
    that randomly generated ones aren't accepted.
    """
    return str(uuid.uuid4()).upper()


class ApiClient:
    """
    Generic API Client for the Venmo API

    Args:
        access_token (str | None, optional): access token you received for your
            account, not including the 'Bearer ' prefix (that's added to the request
            header). Defaults to None. None is only valid on initial authorization.
        device_id (str | None, optional): unique device ID. Defaults to None, in
            which case a random one is generated. FYI I don't think random ids work
            anymore.
    """

    def __init__(self, access_token: str | None = None, device_id: str | None = None):
        self.default_headers = orjson.loads(
            (PROJECT_ROOT / "default_headers.json").read_bytes()
        )
        if os.getenv("LOGGING_SESSION"):
            self.session = LoggingSession()
        else:
            self.session = requests.Session()
        self.session.headers.update(self.default_headers)

        self.access_token = access_token
        if access_token:
            self.update_access_token(access_token)

        if not device_id:
            device_id = random_device_id()

        self.update_device_id(device_id)

        self.update_session_id()
        self.configuration = {"host": "https://api.venmo.com/v1"}

    def update_session_id(self):
        self._session_id = str(getrandbits(64))
        self.default_headers.update({"X-Session-ID": self._session_id})
        self.session.headers.update({"X-Session-ID": self._session_id})

    def update_access_token(self, access_token: str):
        self.access_token = access_token
        self.default_headers.update({"Authorization": "Bearer " + self.access_token})
        self.session.headers.update({"Authorization": "Bearer " + self.access_token})

    def update_device_id(self, device_id: str):
        self.device_id = device_id
        self.default_headers.update({"device-id": self.device_id})
        self.session.headers.update({"device-id": self.device_id})

    def call_api(
        self,
        resource_path: str,
        method: str,
        headers: dict = None,
        params: dict = None,
        body: dict = None,
        ok_error_codes: list[int] = None,
    ) -> ValidatedResponse:
        """Calls API on the provided path

        Args:
            resource_path (str): Specific Venmo API path endpoint.
            method (str): HTTP request method
            headers (dict, optional): request headers. Defaults to None, in which
                case the default ones in `default_headers.json` are used.
            query_params (dict, optional): endpoint query parameters. Defaults to None.
            body (dict, optional): JSON payload to send if request is POST/PUT. Defaults
                to None.
            ok_error_codes (list[int], optional): Expected integer error codes that will be
                handled by calling code and which shouldn't raise. Defaults to None.

        Returns:
            ValidatedResponse
        """

        # Update the header with the required values
        headers = headers or {}

        if body:  # POST or PUT
            headers.update({"Content-Type": "application/json; charset=utf-8"})
        url = self.configuration["host"] + resource_path

        if method not in ["POST", "PUT", "GET", "DELETE"]:
            raise InvalidHttpMethodError()

        response = self.session.request(
            method=method, url=url, headers=headers, params=params, json=body
        )
        validated_response = self._validate_response(response, ok_error_codes)
        return validated_response

    @staticmethod
    def _validate_response(
        response: requests.Response, ok_error_codes: list[int] = None
    ) -> ValidatedResponse:
        """
        Validate and build a new validated response.
        """
        headers = response.headers
        try:
            body = response.json()
        except JSONDecodeError:
            body = {}

        built_response = ValidatedResponse(response.status_code, headers, body)

        if response.status_code in range(200, 205) or (
            body and ok_error_codes and body.get("error").get("code") in ok_error_codes
        ):
            return built_response

        elif response.status_code == 400 and body.get("error").get("code") == 283:
            raise ResourceNotFoundError()

        else:
            raise HttpCodeError(response=response)
