
from fastapi import  Depends,   APIRouter
from sqlmodel import   Session, select
from typing import Annotated

from app.database import  get_session
from app import models, schemas
from app.utils import format_response, hash_password

from sqlmodel import select
from fastapi import status
from sqlalchemy.exc import IntegrityError


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)



@router.get('', response_model=dict)
async def get_all_users(session: Annotated[Session, Depends(get_session)]):
    users = session.exec(select(models.User)).all()
    if users:
        user_responses = [schemas.UserRead.model_validate(user) for user in users]

        return format_response(user_responses, "Users fetched successfully")
    
    return format_response([], "No users found", False)



@router.post('', response_model=dict)
async def create_user(user: schemas.UserCreate, session: Annotated[Session, Depends(get_session)]):
    # Check if email already exists
    existing_user = session.exec(select(models.User).where(models.User.email == user.email)).first()
    if existing_user:
        return format_response(None, "Email already exists", status=False)

    # Create new user
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = models.User(**user.model_dump())
    session.add(new_user)
    
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        return format_response(None, "Failed to create user due to a database constraint", status=False)

    session.refresh(new_user)
    user_response = schemas.UserRead.model_validate(new_user)

    return format_response(user_response, "User created successfully")


@router.get('/{id}', response_model=dict)
async def get_single_user(id: int, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(models.User).where(models.User.id == id)).first()
    if user:
        user_response = schemas.UserRead.model_validate(user)
        return format_response(user_response, "User fetched successfully")
    else:
        return format_response(None, "No User found", status=False)

@router.put('/{id}', response_model=dict)
async def edit_user(id: int, user: schemas.UserCreate, session: Annotated[Session, Depends(get_session)]):
    existing_user = session.exec(select(models.User).where(models.User.id == id)).first()
    if existing_user:
        existing_user.email = user.email
        existing_user.password = user.password
        session.commit()
        session.refresh(existing_user)
        user_response = schemas.UserRead.model_validate(existing_user)
        return format_response(user_response, "User updated successfully")
    else:
        return format_response(None, "No User found", status=False)

@router.delete('/{id}', response_model=dict)
async def delete_user(id: int, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(models.User).where(models.User.id == id)).first()
    if user:
        session.delete(user)
        session.commit()
        return format_response(None, "User deleted successfully")
    else:
        return format_response(None, "No User found", status=False)