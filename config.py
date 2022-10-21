""" Server Configurations 

"""

from fastapi import Depends, FastAPI, Request, Response, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import jwt
from decouple import config
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone

frontend_url = "https://fe.mental-health-sd.com"

key = config("KEY", default="")

optional_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth", auto_error=False)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
