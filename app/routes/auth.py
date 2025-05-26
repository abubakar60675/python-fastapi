
from fastapi import  Depends,   APIRouter
from sqlmodel import   Session, select
from typing import Annotated

from app.database import  get_session
from app import models, schemas
from app.utils import format_response, verify_password
from app.oauth2 import create_access_token

from sqlmodel import select
from fastapi import status
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    tags=["Authantication"],
)



@router.post('/login', response_model=dict)
async def login(user_credentials: schemas.UserCreate, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(models.User).where(models.User.email == user_credentials.email)).first()

    if not user:
        return format_response(None, "Invalid credentials", status=False)

    if not verify_password(user_credentials.password, user.password):
        return format_response(None, "Invalid credentials", status=False)
    
    user_response = schemas.UserRead.model_validate(user)

    access_token = create_access_token(data={"user_id": user.id})



    return format_response({**user_response.model_dump(), "access_token": access_token}, "Logged in successfully")
