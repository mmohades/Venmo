from json import JSONDecodeError
from typing import List
from venmo_api import ResourceNotFoundError, InvalidHttpMethodError, HttpCodeError, validate_access_token
import requests
import threading


class ApiClient(object):
    """
    Generic API Client for the Venmo API
    """

    def __init__(self, access_token=None):
        """
        :param access_token: <str> access token you received for your account.
        """
        super().__init__()

        access_token = validate_access_token(access_token=access_token)

        self.access_token = access_token
        self.configuration = {"host": "https://api.venmo.com/v1"}

        self.default_headers = {"User-Agent": "Venmo/7.44.0 (iPhone; iOS 13.0; Scale/2.0)"}
        if self.access_token:
            self.default_headers.update({"Authorization": self.access_token})

        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def update_access_token(self, access_token):
        self.access_token = validate_access_token(access_token=access_token)
        self.default_headers.update({"Authorization": self.access_token})
        self.session.headers.update({"Authorization": self.access_token})

    def call_api(self, resource_path: str, method: str,
                 header_params: dict = None,
                 params: dict = None,
                 body: dict = None,
                 callback=None,
                 ok_error_codes: List[int] = None):

        """
        Makes the HTTP request (Synchronous) and return the deserialized data.
        To make it async multi-threaded, define a callback function.

        :param resource_path: <str> Specific Venmo API path
        :param method: <str> HTTP request method
        :param header_params: <dict> request headers
        :param params: <dict> request parameters (?=)
        :param body: <dict> request body will be send as JSON
        :param callback: <function> Needs to be provided for async
        :param ok_error_codes: <List[int]> A list of integer error codes that you don't want an exception for.
        :return: response: <dict> {'status_code': <int>, 'headers': <dict>, 'body': <dict>}
        """

        if callback is None:
            return self.__call_api(resource_path=resource_path, method=method,
                                   header_params=header_params, params=params,
                                   body=body, callback=callback,
                                   ok_error_codes=ok_error_codes)
        else:
            thread = threading.Thread(target=self.__call_api,
                                      args=(resource_path, method, header_params,
                                            params, body, callback))
        thread.start()
        return thread

    def __call_api(self, resource_path, method,
                   header_params=None, params=None,
                   body=None, callback=None,
                   ok_error_codes: List[int] = None):
        """
        Calls API on the provided path

        :param resource_path: <str> Specific Venmo API path
        :param method: <str> HTTP request method
        :param header_params: <dict> request headers
        :param body: <dict> request body will be send as JSON
        :param callback: <function> Needs to be provided for async
        :param ok_error_codes: <List[int]> A list of integer error codes that you don't want an exception for.

        :return: response: <dict> {'status_code': <int>, 'headers': <dict>, 'body': <dict>}
        """

        # Update the header with the required values
        header_params = header_params or {}

        if body:
            header_params.update({"Content-Type": "application/json"})

        url = self.configuration['host'] + resource_path

        # Use a new session for multi-threaded
        if callback:
            session = requests.Session()
            session.headers.update(self.default_headers)

        else:
            session = self.session

        # perform request and return response
        processed_response = self.request(method, url, session,
                                          header_params=header_params, params=params,
                                          body=body, ok_error_codes=ok_error_codes)

        self.last_response = processed_response

        if callback:
            callback(processed_response)
        else:
            return processed_response

    def request(self, method, url, session,
                header_params=None,
                params=None,
                body=None,
                ok_error_codes: List[int] = None):
        """
        Make a request with the provided information using a requests.session
        :param method:
        :param url:
        :param session:
        :param header_params:
        :param params:
        :param body:
        :param ok_error_codes: <List[int]> A list of integer error codes that you don't want an exception for.

        :return:
        """

        if method not in ['POST', 'PUT', 'GET', 'DELETE']:
            raise InvalidHttpMethodError()

        response = session.request(
            method=method, url=url, headers=header_params, params=params, json=body)

        # Only accepts the 20x status codes.
        validated_response = self.__validate_response(response, ok_error_codes=ok_error_codes)

        return validated_response

    @staticmethod
    def __validate_response(response, ok_error_codes: List[int] = None):
        """
        Validate and build a new validated response.
        :param response:
        :param ok_error_codes: <List[int]> A list of integer error codes that you don't want an exception for.
        :return:
        """
        try:
            body = response.json()
            headers = response.headers
        except JSONDecodeError:
            body = {}
            headers = {}

        built_response = {"status_code": response.status_code, "headers": headers, "body": body}

        if response.status_code in range(200, 205) and response.json:
            return built_response

        elif response.status_code == 400 and response.json().get('error').get('code') == 283:
            raise ResourceNotFoundError()

        else:
            if body and ok_error_codes and body.get('error').get('code') in ok_error_codes:
                return built_response

            raise HttpCodeError(response=response)
