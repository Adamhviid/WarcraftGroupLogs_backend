import os
import requests
from urllib.parse import urlencode


def get_access_token(url: str):
    auth = (os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
    params = {
        "grant_type": "client_credentials",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            url + "/oauth/token",
            headers=headers,
            auth=auth,  # type: ignore
            data=urlencode(params),
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        return str(e)


""" def sod_access_token():
    auth = (os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
    params = {
        "grant_type": "client_credentials",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            "https://sod.warcraftlogs.com/oauth/token",
            headers=headers,
            auth=auth,  # type: ignore
            data=urlencode(params),
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        return str(e)


def retail_access_token():
    auth = (os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
    params = {
        "grant_type": "client_credentials",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            "https://www.warcraftlogs.com/oauth/token",
            headers=headers,
            auth=auth,  # type: ignore
            data=urlencode(params),
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        return str(e)


def cata_accesstoken():
    auth = (os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET"))
    params = {
        "grant_type": "client_credentials",
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            "https://www.cata.warcraftlogs.com/oauth/token",
            headers=headers,
            auth=auth,  # type: ignore
            data=urlencode(params),
        )
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        return str(e)
 """
