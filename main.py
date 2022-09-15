""" Main Server 

Imports all files and defines the paths which would be called from frontend
"""

from config import *
from model import *
from Types import *
import json


############## placeholder ###############
def evaluation():
    pass
##########################################


@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {"message": "Hello World"}


@app.post("/get_response")
@limiter.limit("100/minute")
async def getResults(request: Request, responses: Items):
    inputVector = responses.answers
    return {"message": "t"}