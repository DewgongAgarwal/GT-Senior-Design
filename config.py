""" Server Configurations 

"""

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import jwt
from decouple import config
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

frontend_url = "https://main--shimmering-sable-27cc10.netlify.app"

key = config("KEY", default="")

optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth", auto_error=False)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
