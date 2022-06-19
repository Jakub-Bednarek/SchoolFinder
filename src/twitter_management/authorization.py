import dotenv
import os

from requests_oauthlib import OAuth1Session
from helpers.logger import log_err, log_wrn

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
BASE_AUTHORIZATION_URL = "https://api.twitter.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://api.twitter.com/oauth/access_token"


class InvalidPinException(Exception):
    pass


class Authenticator:
    def __init__(self):
        dotenv.load_dotenv()
        self.__api_key = None
        self.__api_secret = None
        self.__oauth = None
        self.__oauth_token = None
        self.__oauth_secret = None
        self.__access_token = None
        self.__access_secret = None
        self.get_api_keys()

    def get_api_keys(self):
        self.__api_key = os.getenv("API_KEY")
        self.__api_secret = os.getenv("API_SECRET")

    def fetch_api_oauth_tokens(self):
        self.__oauth = OAuth1Session(self.__api_key, self.__api_secret)
        try:
            fetch_response = self.__oauth.fetch_request_token(REQUEST_TOKEN_URL)
        except ValueError as e:
            log_err(f"Failed to authenticate with API keys, exiting")
            pass

        self.__oauth_token = fetch_response.get("oauth_token")
        self.__oauth_secret = fetch_response.get("oauth_token_secret")

    def get_authorization_url(self):
        return self.__oauth.authorization_url(BASE_AUTHORIZATION_URL)

    def get_access_token(self):
        return self.__access_token

    def get_access_token_secret(self):
        return self.__access_secret

    def sign_in_with_pin(self, pin: str):
        oauth = OAuth1Session(
            self.__api_key,
            client_secret=self.__api_secret,
            resource_owner_key=self.__oauth_token,
            resource_owner_secret=self.__oauth_secret,
            verifier=pin,
        )

        try:
            oauth_tokens = oauth.fetch_access_token(ACCESS_TOKEN_URL)
        except Exception as e:
            raise InvalidPinException("Couldn't authenticate user with PIN!")

        self.__access_token = oauth_tokens["oauth_token"]
        self.__access_secret = oauth_tokens["oauth_token_secret"]

        print(self.__access_token)
        print(self.__access_secret)


authenticator = Authenticator()
authenticator.fetch_api_oauth_tokens()
