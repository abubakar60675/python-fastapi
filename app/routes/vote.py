
from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter, Query
from sqlmodel import SQLModel, create_engine, Session, select, func
from typing import Annotated
from contextlib import asynccontextmanager

from app.database import create_tables, get_session
from app import models, schemas
from app.utils import format_response, hash_password

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from sqlmodel import select
from fastapi import status
from sqlalchemy.exc import IntegrityError
from app.oauth2 import get_current_user


router = APIRouter(
    prefix="/vote",
    tags=["Votes"],
)


@router.post('', response_model=dict)
def create_vote(
    vote: schemas.Vote,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[schemas.TokenData, Depends(get_current_user)]
):
    post = session.exec(select(models.Post).where(models.Post.id == vote.post_id)).first()
    if not post:
        
        return format_response(None, f"Post with id {vote.post_id} does not exist", False)

    existing_vote = session.exec(
        select(models.Vote).where(
            models.Vote.post_id == vote.post_id,
            models.Vote.user_id == current_user.id
        )
    ).first()

    if vote.dir == 1:
        if existing_vote:
            return format_response(None, f"User {current_user.id} has already voted on post {vote.post_id}", status=False)
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        session.add(new_vote)
        session.commit()
        return format_response(None, "Vote created successfully")
    else:
        if not existing_vote:
            return format_response(None, "Vote does not exist", status=False)
        session.delete(existing_vote)
        session.commit()
        return format_response(None, "Vote deleted successfully")