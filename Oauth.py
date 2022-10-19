from cas import CASClient
from typing import Optional
from fastapi import *
from config import *
from model import totalUnverified

user = None
authorizedUsers = ["dagarwal47"]


cas_client = CASClient(
    version=2,
    server_url="https://login.gatech.edu/cas/login",
    service_url="https://sd-be.herokuapp.com/login",
)


def check_token(auth_token):
    try:
        auth_token = jwt.decode(auth_token, key, algorithms="HS256")
        print(auth_token["user"])
        print(user)
        return user == auth_token["user"] and auth_token["user"] in authorizedUsers
    except Exception as e:
        return False


def _add_cookie_to_reponse(response, params):
    for i in params:
        response.set_cookie(key=i, value=params[i])


def auth_token_generator(payload=None):
    return jwt.encode(
        {
            "user": user,
            "exp": int((datetime.now() + timedelta(minutes=5)).timestamp()),
        },
        key,
        algorithm="HS256",
    )


def refresh(request: Request, response: Response, token):
    if token is not None:

        try:
            print(token)
            auth_token = jwt.decode(token, key, algorithms="HS256")
            if user == auth_token["user"] and auth_token["user"] not in authorizedUsers:
                raise Exception("Unauthorized User")
            token = auth_token_generator()
            return {"authToken": token}
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": "Login Again", "redirect_url": f"/logout"}

def login(request: Request, ticket: Optional[str] = None):
    global user
    if not ticket:
        cas_login_url = cas_client.get_login_url()
        print(cas_login_url)
        return {"redirect_url": cas_login_url, "requestType": "CAS"}

    user, attributes, pgtiou = cas_client.verify_ticket(ticket)
    print(user)

    if not user or user not in authorizedUsers:
        response = RedirectResponse(frontend_url)
        _add_cookie_to_reponse(
            response, {"message": "Login Failed / Unauthorized Access"}
        )
        return response
    else:
        auth_token = auth_token_generator()
        response = RedirectResponse(frontend_url)
        _add_cookie_to_reponse(
            response, {"message": "Login Success.", "authToken": auth_token, "total": totalUnverified()}
        )
        return response


def logout(request: Request):
    global user
    user = None
    cas_logout_url = cas_client.get_logout_url()
    return {
        "redirect_url": cas_logout_url,
        "requestType": "CAS",
        "message": "Logout Success.",
    }
