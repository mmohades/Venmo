import requests
import json
import threading


class ApiClient(object):
    """
    Generic API Client for the Venmo API
    """

    def __init__(self, access_token=None):

        self.access_token = access_token
        self.configuration = {"host": "https://api.venmo.com/v1"}
        self.default_headers = {"Authorization": f"Barear {self.access_token}",
                                "User-Agent": "Venmo/7.29.1 (iPhone; iOS 13.0; Scale/2.0)"}
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)

    def call_api(self, resource_path, method, params=None,
                 header_params=None, body=None, auth_settings=None, callback=None):
        """
        Makes the HTTP request (Synchronous) and return the deserilized data.
        To make it async, define a callback function.
        """
        if callback is None:
            return self.__call_api(resource_path, method,
                                   header_params, body,
                                   callback)
        else:
            thread = threading.Thread(target=self.__call_api,
                                      args=(resource_path, method,
                                            params, header_params,
                                            body, auth_settings, callback))
        thread.start()
        return thread

    def __call_api(self, resource_path, method,
                   header_params=None, body=None,
                   callback=None):
        """
        resource_path: url
        method: Request verb
        header_params: Request header parameteres
        body: Json body
        callback: Callback method for the async calls
        """

        # Update the header with the required values
        header_params = header_params or {}
        if body:
            header_params.update({"Content-Type": "application/json"})

        url = self.configuration['host'] + resource_path

        # Use a new session if it's threaded
        if callback:
            session = requests.Session()
            session.headers.update(self.default_headers)

        else:
            session = self.session
            header_params.update({'Connection': 'keep-alive'})

        # perform request and return response
        response_data, response_type = self.request(method, url, session,
                                                    header_params=header_params,
                                                    body=body)

        self.last_response = response_data

        # deserialize response data
        deserialized_data = self.deserialize(response_data, response_type)

        if callback:
            callback(deserialized_data)
        else:
            return deserialized_data

    def request(self, method, url, session, header_params=None, body=None):

        if method not in ['POST', 'PUT', 'GET' 'DELETE']:
            # TODO: Raise method is not valid exception here and make the exceptions
            return "Method is not valid"

            # Sanitize?
        response = session.request(
            method=method, url=url, headers=header_params, json=body)

    def deserialize(self, response_data, response_type):
        return {}
