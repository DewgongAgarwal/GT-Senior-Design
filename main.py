""" Main Server 

Imports all files and defines the paths which would be called from frontend
"""
from dotenv import load_dotenv

load_dotenv()

from config import *
from model import *
from Types import *
import Oauth
import json
from disjoint_LinUCB import *


@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {"message": "Hello World"}


@app.post("/get_response")
@limiter.limit("100/minute")
async def getResults(
    request: Request, responses: Items, background_tasks: BackgroundTasks
):
    inputVector = responses.answers
    prediction = get_prediction(inputVector)
    background_tasks.add_task(
        add_response_to_db, responses=inputVector, predictionGiven=prediction
    )
    return {"message": prediction}


@app.get("/login")
@limiter.limit("100/minute")
async def login(
    request: Request, background_tasks: BackgroundTasks, ticket: Optional[str] = None
):
    print("here")
    return Oauth.login(request, background_tasks, ticket)


@app.post("/logout")
@limiter.limit("100/minute")
async def logout(
    request: Request, background_tasks: BackgroundTasks, responses: AuthKeys
):
    return Oauth.logout(request, background_tasks, responses.token)


@app.post("/refreshToken")
@limiter.limit("100/minute")
async def refresh(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    responses: AuthKeys,
):
    return Oauth.refresh(request, response, background_tasks, responses.token)


@app.post("/getNext")
@limiter.limit("100/minute")
async def next(request: Request, response: Response, responses: AuthKeys):
    print(responses.token)
    if Oauth.check_token(responses.token):
        response = dict(read_next_invalidated())
        if "data" in response and not response["data"]:
            print(response)
        else:
            del response["_sa_instance_state"]
            print(response)
        return response
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Unauthorized Access."}


@app.post("/updateForm")
@limiter.limit("100/minute")
async def updateForm(request: Request, response: Response, responses: Validation):
    if Oauth.check_token(responses.token):
        questions = updatePrediction(responses.id, responses.actual)
        if questions[0] is not None and questions[1] is not None:
            update_model_parameters(
                list(map(int, list(questions[0]))), questions[1], responses.actual
            )
        return {"message": "Submitted"}
    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": "Unauthorized Access."}


# @app.get("/reset")
# @limiter.limit("100/minute")
# async def reset(request: Request):
#     resetDb()
