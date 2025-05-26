import jwt
from jwt.exceptions import InvalidTokenError

from datetime import datetime, timedelta, timezone
from app import models, schemas

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials

from sqlmodel import  Session, select
from app.database import  get_session
from app.config import settings


from typing import Annotated


oauth2_scheme = HTTPBearer()



SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES



def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("user_id")
        if id is None:
           raise  credentials_exception

        token_data = schemas.TokenData(id=id)
        
    except InvalidTokenError:
        raise credentials_exception
    
    return token_data


async def get_current_user(token: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(f"here: {token}")
    token_data = verify_access_token(token.credentials, credentials_exception)
    user = session.exec(select(models.User).where(models.User.id == token_data.id)).first()

    return user