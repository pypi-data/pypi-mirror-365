from requests.auth import HTTPBasicAuth


class CollibraConnector():
    """
    This class is used to connect to the Collibra API.
    It requires the API URL and authentication credentials.
    The authentication is done using HTTP Basic Auth.
    """

    def __init__(self, api: str, username: str, password: str):
        """
        Initializes the CollibraConnector with API URL and authentication credentials.
        :param api: The API URL for Collibra.
        :param username: The username for authentication.
        :param password: The password for authentication.
        """
        self.__auth = HTTPBasicAuth(username, password)
        self.__api = api + "/rest/2.0"
        self.__base_url = api

    def __repr__(self):
        return f"CollibraConnector(api={self.__api}, auth={self.__auth})"

    @property
    def api(self):
        return self.__api

    @property
    def auth(self):
        return self.__auth

    @property
    def base_url(self):
        return self.__base_url