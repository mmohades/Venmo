from venmo_api.apis.api_client import ApiClient
from venmo_api.apis.api_util import ValidatedResponse, deserialize
from venmo_api.models.page import Page
from venmo_api.models.transaction import Transaction
from venmo_api.models.user import User


class UserApi:
    """API for querying users and transactions.

    Args:
        api_client (ApiClient): Logged in client instance to use for requests.
    """

    def __init__(self, api_client: ApiClient):
        self.__api_client = api_client
        self._profile = None
        self._balance = None

    def get_my_profile(self, force_update=False) -> User:
        """Get your profile info and return as a User.

        Args:
            force_update (bool, optional): Whether to require fetching updated data from
                API. Defaults to False.

        Returns:
            User: Your profile.
        """
        if self._profile and not force_update:
            return self._profile

        response = self.__api_client.call_api(resource_path="/account", method="GET")
        self._profile = deserialize(response, User, nested_response=["user"])
        return self._profile

    def get_my_balance(self, force_update=False) -> float:
        """Get your current balance info and return as a float.

        Args:
            force_update (bool, optional): Whether to require fetching updated data from
                API. Defaults to False.

        Returns:
            float: Your balance
        """
        if self._balance and not force_update:
            return self._balance

        response = self.__api_client.call_api(resource_path="/account", method="GET")
        self._balance = deserialize(response, float, nested_response=["balance"])
        return self._balance

    # --- USERS ---

    def search_for_users(
        self,
        query: str,
        offset: int = 0,
        limit: int = 50,
        username: bool = False,
    ) -> Page[User]:
        """search for [query] in users

        Args:
            query (str): user search terms.
            offset (int, optional): Page offset. Defaults to 0.
            limit (int, optional): Maximum number of entries to return. Defaults to 50.
            username (bool, optional): Pass True if search is by username. Defaults to False.

        Returns:
            Page[User]: A list of User objects or empty
        """

        params = {"query": query, "limit": limit, "offset": offset}
        # update params for querying by username
        if username or "@" in query:
            params.update({"query": query.replace("@", ""), "type": "username"})

        response = self.__api_client.call_api(
            resource_path="/users", params=params, method="GET"
        )
        return deserialize(response=response, data_type=User).set_method(
            method=self.search_for_users,
            kwargs={"query": query, "limit": limit},
            current_offset=offset,
        )

    def get_user(self, user_id: str) -> User | None:
        """Get the user profile with [user_id]

        Args:
            user_id (str): uuid for user, as returned by User.id.

        Returns:
            User | None: the corresponding User, if any.
        """
        response = self.__api_client.call_api(
            resource_path=f"/users/{user_id}", method="GET"
        )
        try:
            return deserialize(response=response, data_type=User)
        except Exception:
            return None

    def get_user_by_username(self, username: str) -> User | None:
        """Search for the user profile with [username]

        Args:
            username (str): username of User.

        Returns:
            User | None: The corresponding User, if any.
        """
        users = self.search_for_users(query=username, username=True)
        for user in users:
            if user.username == username:
                return user

        # username not found
        return None

    def get_user_friends_list(
        self,
        user_id: str,
        offset: int = 0,
        limit: int = 3337,
    ) -> Page[User]:
        """Get [user_id]'s friends list as a list of Users

        Args:
            user_id (str): uuid for user, as returned by User.id.
            offset (int, optional): Page offset. Defaults to 0.
            limit (int, optional): Maximum number of entries to return. Defaults to 3337.

        Returns:
            Page[User]: A list of User objects or empty if no friends :(
        """
        params = {"limit": limit, "offset": offset}
        response = self.__api_client.call_api(
            resource_path=f"/users/{user_id}/friends", method="GET", params=params
        )
        return deserialize(response=response, data_type=User).set_method(
            method=self.get_user_friends_list,
            kwargs={"user_id": user_id, "limit": limit},
            current_offset=offset,
        )

    # --- TRANSACTIONS ---

    def get_user_transactions(
        self,
        user_id: str,
        social_only: bool = False,
        public_only: bool = True,
        limit: int = 50,
        before_id: str | None = None,
    ) -> Page[Transaction]:
        """Get [user_id]'s transactions visible to you as a list of Transactions

        Args:
            user_id (str): uuid for user, as returned by User.id.
            social_only (bool, optional): I think this means show only transactions
                between personal accounts, not business/charity ones, but haven't
                verified. Defaults to False.
            public_only (bool, optional): I think this means show only transactions
                the user has made public, but haven't verified. Defaults to True.
            limit (int, optional): Maximum number of entries to return. Defaults to 50.
            before_id (str | None, optional): Index for determining the page returned.
                Defaults to None.

        Returns:
            Page[Transaction]: A list of Transaction objects.
        """
        response = self._get_transactions(
            user_id, social_only, public_only, limit, before_id
        )
        return deserialize(response, Transaction).set_method(
            method=self.get_user_transactions,
            kwargs={
                "user_id": user_id,
                "social_only": social_only,
                "public_only": public_only,
                "limit": limit,
            },
        )

    def get_friends_transactions(
        self,
        social_only: bool = False,
        public_only: bool = True,
        limit: int = 50,
        before_id: str | None = None,
    ) -> Page[Transaction]:
        """Get your friends' transactions visible to you as a list of Transactions

        Args:
            social_only (bool, optional): I think this means show only transactions
                between personal accounts, not business/charity ones, but haven't
                verified. Defaults to False.
            public_only (bool, optional): I think this means show only transactions
                the user has made public, but haven't verified. Defaults to True.
            limit (int, optional): Maximum number of entries to return. Defaults to 50.
            before_id (str | None, optional): Index for determining the page returned.
                Defaults to None.

        Returns:
            Page[Transaction]: A list of Transaction objects.
        """
        response = self._get_transactions(
            "friends", social_only, public_only, limit, before_id
        )
        return deserialize(response, Transaction).set_method(
            method=self.get_friends_transactions,
            kwargs={
                "social_only": social_only,
                "public_only": public_only,
                "limit": limit,
            },
        )

    def get_transaction_between_two_users(
        self,
        user_id_one: str,
        user_id_two: str,
        social_only: bool = False,
        public_only: bool = True,
        limit: int = 50,
        before_id: str | None = None,
    ) -> Page[Transaction] | None:
        """Get the transactions between two users. Note that user_one_id must be the owner
        of the access token. Otherwise it raises an unauthorized error.

        Args:
            user_id_one (str): Your user uuid.
            user_id_two (str): uuid of the other person
            social_only (bool, optional): I think this means show only transactions
                between personal accounts, not business/charity ones, but haven't
                verified. Defaults to False.
            public_only (bool, optional): I think this means show only transactions
                the user has made public, but haven't verified. Defaults to True.
            limit (int, optional): Maximum number of entries to return. Defaults to 50.
            before_id (str | None, optional): Index for determining the page returned.
                Defaults to None.

        Returns:
            Page[Transaction]: A list of Transaction objects.
        """
        response = self._get_transactions(
            f"{user_id_one}/target-or-actor/{user_id_two}",
            social_only,
            public_only,
            limit,
            before_id,
        )
        return deserialize(response, Transaction).set_method(
            method=self.get_transaction_between_two_users,
            kwargs={
                "user_id_one": user_id_one,
                "user_id_two": user_id_two,
                "social_only": social_only,
                "public_only": public_only,
                "limit": limit,
            },
        )

    def _get_transactions(
        self,
        endpoint_suffix: str,
        social_only: bool,
        public_only: bool,
        limit: int,
        before_id: str | None,
    ) -> ValidatedResponse | None:
        """ """
        params = {
            "limit": limit,
            "social_only": str(social_only).lower(),
            "only_public_stories": str(public_only).lower(),
        }
        if before_id:
            params["before_id"] = before_id

        # Make the request
        response = self.__api_client.call_api(
            resource_path=f"/stories/target-or-actor/{endpoint_suffix}",
            method="GET",
            params=params,
        )
        return response
