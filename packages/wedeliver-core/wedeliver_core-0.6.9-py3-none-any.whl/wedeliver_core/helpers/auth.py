import json
import requests
from flask import request
from .exceptions import AppValidationError,AppMissingAuthError
from flask import session

from .. import WeDeliverCore


class Auth:
    def __init__(self):
        pass

    @staticmethod
    def set_user(user):

        user["is_admin"] = user.get("role") == "Administrator"

        if request.headers.get("Accept-Language") in ("ar", "en"):
            user["language"] = request.headers.get("Accept-Language")
        else:
            user["language"] = user.get("language", "ar")

        app = WeDeliverCore.get_app()
        app.logger.debug(user)
        session["user"] = user

    @staticmethod
    def get_user():
        default_user_str = 'Guest'
        try:
            user = session.get("user", dict())
        except Exception:
            user = dict(user_id=default_user_str, email=default_user_str)

        return user

    @staticmethod
    def get_user_str():
        # app = WeDeliverCore.get_app()
        # with app.test_request_context():
        user = Auth.get_user()

        if user.get('role') == 'captain':
            return "{} : {} : {}".format(
                user.get("captain_id"),
                user.get("full_name"),
                user.get("mobile"),
            )
        else:
            return user.get('email')


def verify_user_token(token,allowed_permissions=None):
    app = WeDeliverCore.get_app()
    allowed_permissions_url = "[]"
    if allowed_permissions:
        allowed_permissions_url = "&allowed_permissions=[{}]".format(",".join(allowed_permissions))

    url = "{authenticate_url}".format(
        authenticate_url="{0}/api/v1/authenticate".format(
            app.config.get("AUTH_SERVICE")
        )
    ) + "?token={token}{allowed_permissions_url}".format(token =token,allowed_permissions_url=allowed_permissions_url)

    app.logger.debug(url)

    lang = None
    try:
        lang = (
            request.headers["Accept-Language"].lower()
            if (
                    "Accept-Language" in request.headers
                    and request.headers["Accept-Language"]
            )
            else Auth.get_user().get("language")
        )
    except Exception:
        pass

    language = lang or "ar"

    response = requests.request(
        "GET", url, headers={"Accept-Language": language}, data=dict()
    )

    if response.status_code != 200:
        raise AppValidationError("Invalid Token")

    try:
        response = json.loads(response.text)
    except Exception:
        raise AppValidationError("Error in parsing auth response")

    if not response.get("success"):
        raise AppValidationError("Invalid Token, {0}".format(response.get("success")))

    response["data"]["token"] = token
    user = response["data"]
    Auth.set_user(user)
        # will check from the AUTH if the user has the requested allowed_permissions above 
        # if the user has the permission then will return true else will return false
    # if not response.get("is_valid_permission"):
    #     raise AppMissingAuthError("You have not enough permission in your role")
    return user
