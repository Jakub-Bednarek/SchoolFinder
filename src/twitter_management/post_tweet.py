import os

from requests_oauthlib import OAuth1Session
from twitter_management.authorization import authenticator

POST_URL = "https://api.twitter.com/2/tweets"


class TweetNotPostedException(Exception):
    pass


def get_api_keys():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    return api_key, api_secret


def post(content):
    keys = get_api_keys()
    access_token = authenticator.get_access_token()
    access_token_secret = authenticator.get_access_token_secret()
    oauth = OAuth1Session(
        keys[0],
        client_secret=keys[1],
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )

    return oauth.post(POST_URL, json=content)


def check_return_code(response):
    if response.status_code != 201:
        raise TweetNotPostedException(
            f"Request returned an error: {response.status_code}, {response.text}"
        )
