""" Main Server 

Imports all files and defines the paths which would be called from frontend
"""

from config import *
from model import *
from Types import *


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
async def getResults(request: Request):
    print(request)
    # result = evaluation(responses)
    return {"message": "t"}