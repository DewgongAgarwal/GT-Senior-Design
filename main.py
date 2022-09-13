from config import *
from model import *

@app.get("/")
@limiter.limit("100/minute")
async def root(request: Request):
    return {"message": "Hello World"}