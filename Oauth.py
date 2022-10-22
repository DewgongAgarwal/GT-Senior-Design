from cas import CASClient
from typing import Optional
from fastapi import *
from config import *
from model import *

authorizedUsers = []

cas_client = CASClient(
    version=2,
    server_url="https://login.gatech.edu/cas/login",
    service_url="http://localhost:8000/login",
)


def check_token(token):
    try:
        auth_token = jwt.decode(token, key, algorithms="HS256")
        return check_user(
            auth_token["user"], token
        )  # and auth_token["user"] in authorizedUsers
    except Exception as e:
        return False


def _add_cookie_to_reponse(response, params):
    for i in params:
        response.set_cookie(key=i, value=params[i])
        # response.set_cookie(key=i, value=params[i], domain=".mental-health-sd.com")


def auth_token_generator(user):
    return jwt.encode(
        {
            "user": user,
            "exp": int((datetime.now() + timedelta(seconds=1800)).timestamp()),
        },
        key,
        algorithm="HS256",
    )


def refresh(
    request: Request, response: Response, background_tasks: BackgroundTasks, token
):
    if token is not None:
        try:
            auth_token = jwt.decode(token, key, algorithms="HS256")
            if not check_user(
                auth_token["user"], token
            ):  # and auth_token["user"] not in authorizedUsers:
                raise Exception("Unauthorized User")
            token = auth_token_generator(auth_token["user"])
            background_tasks.add_task(update_authToken, auth_token["user"], token)
            return {"authToken": token}
        except Exception as e:
            print(e)
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Login Again", "redirect_url": f"/logout"}
    return {"message": "Login Again", "redirect_url": f"/logout"}


def login(
    request: Request, background_tasks: BackgroundTasks, ticket: Optional[str] = None
):
    if not ticket:
        cas_login_url = cas_client.get_login_url()
        return {"redirect_url": cas_login_url, "requestType": "CAS"}

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)

    if not user:  # or user not in authorizedUsers:
        response = RedirectResponse(frontend_url)
        _add_cookie_to_reponse(
            response, {"message": "Login Failed / Unauthorized Access"}
        )
        return response
    else:
        auth_token = auth_token_generator(user)
        background_tasks.add_task(add_to_user, user, auth_token)
        response = RedirectResponse(frontend_url)
        _add_cookie_to_reponse(
            response,
            {
                "message": "Login Success.",
                "authToken": auth_token,
                "total": totalUnverified(),
            },
        )
        return response

def force_logout(message):
    cas_logout_url = cas_client.get_logout_url()
    return {
        "redirect_url": cas_logout_url,
        "requestType": "CAS",
        "message": message,
    }

def logout(request: Request, background_tasks: BackgroundTasks, token):

    if token is not None:
        try:
            auth_token = jwt.decode(token, key, algorithms="HS256")
            if not check_user(
                auth_token["user"], token
            ):  # and auth_token["user"] not in authorizedUsers:
                raise Exception("Unauthorized User")
            background_tasks.add_task(remove_from_user, auth_token["user"])
        finally:
            return force_logout("Logout Success.")
