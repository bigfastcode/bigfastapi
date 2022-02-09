import os

from datetime import datetime
from datetime import timedelta

import jwt
from fastapi import Depends, APIRouter
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse


app = APIRouter(tags=["Social_Auth"])

# Create the auth app
auth_app = FastAPI()

FAKE_DB = {'disutj@gmail.com': {'name': 'Disu Oluwatoyin'}}
# OAuth settings
GOOGLE_CLIENT_ID="620824813671-47q9fct9om4033h6p2pn6n3em3nmub4s.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="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"
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Set up the middleware to read the request session
SECRET_KEY = "yeahyeh500500"
if SECRET_KEY is None:
    raise 'Missing SECRET_KEY'

auth_app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Frontend URL:
FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://127.0.0.1:7001/google/token'

@app.route('/google/login')
async def login(request: Request):
    redirect_uri = FRONTEND_URL  # This creates the url for our /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/google/token')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        raise CREDENTIALS_EXCEPTION
    user_data = await oauth.google.parse_id_token(request, access_token)
    if valid_email_from_db(user_data['email']):
        return JSONResponse({'result': True, 'access_token': create_token(user_data['email'])})
    raise CREDENTIALS_EXCEPTION

@app.get('/current')
def public(request: Request):
    user = request.session.get('user')
    if user:
        print(user)
    return JSONResponse({"user": user})


def cast_to_number(id):
    temp = os.environ.get(id)
    if temp is not None:
        try:
            return float(temp)
        except ValueError:
            return None
    return None


# Configuration
API_SECRET_KEY = "uyyeujnfbhgdtwyuiofkjhndbwgyufiklew"
if API_SECRET_KEY is None:
    raise BaseException('Missing API_SECRET_KEY env var.')
API_ALGORITHM = os.environ.get('API_ALGORITHM') or 'HS256'
API_ACCESS_TOKEN_EXPIRE_MINUTES = cast_to_number('API_ACCESS_TOKEN_EXPIRE_MINUTES') or 15

# Token url (We should later create a token url that accepts just a user and a password to use it with Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

# Error
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)


# Create token internal function
def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, API_SECRET_KEY, algorithm=API_ALGORITHM)
    return encoded_jwt


# Create token for an email
def create_token(email):
    access_token_expires = timedelta(minutes=API_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': email}, expires_delta=access_token_expires)
    return access_token


def valid_email_from_db(email):
    return email in FAKE_DB


async def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[API_ALGORITHM])
        email: str = payload.get('sub')
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except jwt.PyJWTError:
        raise CREDENTIALS_EXCEPTION

    if valid_email_from_db(email):
        return email

    raise CREDENTIALS_EXCEPTION
