import os
from typing import Self

from venmo_api import ApiClient, AuthenticationApi, PaymentApi, UserApi
from venmo_api.models.user import User


class Client:
    """User-friendly VenmoAPI Client. `Client.login()` is the recommended way to
    instantiate rather than calling `Client()` directly.

    ```
    with Client.login(user, pw, dev_id) as client:
        client.pay_your_people()
    # now you're automatically logged out, no worries of active access tokens floating
    # around in the ether to keep you up at night.
    ```
    """

    @staticmethod
    def login_from_env(
        username_env: str, password_env: str, device_id_env: str
    ) -> Self:
        """Convenience method to login from loaded environment variables.

        Args:
            username_env (str): Env var for username.
            password_env (str): Env var for password.
            device_id_env (str): Env var for device ID.

        Returns:
            Self: Logged in Client instance.
        """

        return Client.login(
            os.getenv(username_env), os.getenv(password_env), os.getenv(device_id_env)
        )

    @staticmethod
    def login(username: str, password: str, device_id: str | None = None) -> Self:
        """Log in using your credentials and get an access_token to use in the API.
        Recommended way to instantiate a Client.

        Args:
            username (str): Can be username, phone number (without +1) or email address.
            password (str): Account's password.
            device_id (str | None, optional): A valid device-id. Defaults to None. FYI I
                think it's not actually optional anymore.

        Returns:
            Self: Logged in Client instance.
        """
        api_client = ApiClient(device_id=device_id)
        # api_client is updated with access_token internally
        access_token = AuthenticationApi(api_client).login_with_credentials_cli(
            username=username, password=password
        )
        return Client(api_client=api_client)

    @staticmethod
    def logout(access_token) -> bool:
        """Revoke your access_token. Log out, in other words.

        Args:
            access_token (_type_): Token for current session.

        Returns:
            bool: True or raises exception.
        """
        return AuthenticationApi.log_out(access_token=access_token)

    def __init__(
        self,
        access_token: str | None = None,
        device_id: str | None = None,
        api_client: ApiClient | None = None,
    ):
        """
        Args:
            access_token (str | None, optional): Token for already logged in session, if
                available. Defaults to None. This is only optional because you can
                choose to pass an initialized ApiClient holding the token instead.
            device_id (str | None, optional):  A valid device-id. Defaults to None. This
                is only optional because you can choose to pass an initialized ApiClient
                holding the id instead.
            api_client (ApiClient | None, optional): Alternative to the above 2.
                Defaults to None.
        """
        if api_client is None:
            self.__api_client = ApiClient(
                access_token=access_token, device_id=device_id
            )
        else:
            # NOTE: for anything sensitive, makes sense to pass ApiClient instance that
            # you logged in with, since it stores the original csrf_token set at login.
            # Haven't verified that this is absolutely necessary, but seems sensible to
            # align with the app's behavior.
            self.__api_client = api_client
            if access_token is not None:
                # don't allow the possibility of clearing an already set token
                self.__api_client.update_access_token(access_token)

        self.user = UserApi(self.__api_client)
        self._profile = self.user.get_my_profile()
        self._balance = self.user.get_my_balance()
        self.payment = PaymentApi(
            profile=self._profile, api_client=self.__api_client, balance=self._balance
        )

    def my_profile(self, force_update=False) -> User:
        """Get your profile info. It can be cached from the previous time.

        Args:
            force_update (bool, optional): Whether to force fetching an updated user.
                Defaults to False.

        Returns:
            User: your profile.
        """
        if force_update:
            self._profile = self.user.get_my_profile(force_update=force_update)

        return self._profile

    def my_balance(self, force_update=False) -> float:
        """Get your Venmo balance. It can be cached from the previous time.

        Args:
            force_update (bool, optional): Whether to force fetching an updated balance.
                Defaults to False.

        Returns:
            float: your balance.
        """
        if force_update:
            self._balance = self.user.get_my_balance(force_update=force_update)

        return self._balance

    @property
    def access_token(self) -> str | None:
        return self.__api_client.access_token

    # context manager dunder methods for `with` block logout using stored token
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.log_out_instance()

    def log_out_instance(self) -> bool:
        """Convenience instance method for logging out using stored access token. Called
        automatically at conclusion of a with block.

        Returns:
            bool: True or exceptionm raised
        """
        return AuthenticationApi.log_out(self.access_token)
