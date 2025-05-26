
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
    prefix="/posts",
    tags=["Posts"],
)



# @router.get('')
# async def get_all(session: Annotated[Session, Depends(get_session)],current_user: Annotated[schemas.TokenData, Depends(get_current_user)]):
#     print(f"current_user: {current_user.model_dump()}")
#     posts = session.exec(select(models.Post)).all()
#     if posts:
#         posts_responses = [schemas.PostRead.model_validate(posts) for posts in posts]
#         return format_response(posts_responses, "Posts fetched successfully")
#     return format_response([], "No posts found", False)

# @router.get("", response_model=dict)
# async def get_all(
#     session: Annotated[Session, Depends(get_session)],
#     current_user: Annotated[schemas.TokenData, Depends(get_current_user)],
#     skip: int = Query(0, ge=0),
#     limit: int = Query(10, ge=1),
#     search: str = Query("", alias="search")
# ):
#     print(f"current_user: {current_user.model_dump()}")

#     # Base query
#     base_query = select(models.Post)

#     if search:
#         base_query = base_query.where(models.Post.title.contains(search))

#     # Total count
#     total_count = session.exec(
#         select(func.count()).select_from(base_query.subquery())
#     ).one()

#     # Paginated rows
#     posts = session.exec(base_query.offset(skip).limit(limit)).all()
#     rows = [schemas.PostRead.model_validate(post) for post in posts]

#     return format_response({
#         "rows": rows,
#         "totalCount": total_count
#     }, "Posts fetched successfully")

@router.get("", response_model=dict)
async def get_all(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[schemas.TokenData, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: str = Query("", alias="search")
):
    # Aliases
    Post = models.Post
    Vote = models.Vote

    # Query posts + vote counts
    stmt = (
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .where(Post.title.contains(search))
        .group_by(Post.id)
        .offset(skip)
        .limit(limit)
    )
    results = session.exec(stmt).all()

    # Total count
    total_count_stmt = (
        select(func.count())
        .select_from(Post)
        .where(Post.title.contains(search))
    )
    total_count = session.exec(total_count_stmt).one()

    # Merge each post and its vote count
    rows = []
    for post, votes in results:
        post_dict = schemas.PostRead.model_validate(post).model_dump()
        post_dict["votes"] = votes
        rows.append(post_dict)

    return format_response({
        "rows": rows,
        "totalCount": total_count
    }, "Posts fetched successfully")

@router.post('', response_model=dict)
async def create_post(
post: schemas.PostCreate, 
session: Annotated[Session, Depends(get_session)],
current_user: Annotated[schemas.TokenData, Depends(get_current_user)]):

    print(f"bro: {current_user.model_dump()}")

    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)

    post_response = schemas.PostRead.model_validate(new_post)

    return format_response(post_response, "Post created successfully")


@router.get('/{id}', response_model=dict)
async def get_single_post(id: int, session: Annotated[Session, Depends(get_session)],current_user: Annotated[schemas.TokenData, Depends(get_current_user)]):

    Post = models.Post
    Vote = models.Vote    
    stmt = (
        select(Post, func.count(Vote.post_id).label("votes"))
        .join(Vote, Vote.post_id == Post.id, isouter=True)
        .where(Post.id == id)
        .group_by(Post.id)
    )
    result = session.exec(stmt).first()

    if not result:
        return format_response(None, "No Post found", status=False)
    
    post, votes = result

    if post.owner_id != current_user.id:
        return format_response(None, "You are not authorized to perform this action", status=False)
    
    post_response = schemas.PostRead.model_validate(post).model_dump()
    post_response["votes"] = votes

    return format_response(post_response, "Post fetched successfully")


@router.put('/{id}',response_model=dict)
async def edit_post(id: int, post: schemas.PostCreate, session: Annotated[Session, Depends(get_session)],current_user: Annotated[schemas.TokenData, Depends(get_current_user)]):
    existing_post = session.exec(select(models.Post).where(models.Post.id == id)).first()

    if not existing_post:
        return format_response(None, "No Post found", status=False)

    if existing_post.owner_id != current_user.id:
        return format_response(None, "You are not authorized to perform this action", status=False)
    

    existing_post.title = post.title
    existing_post.content = post.content
    existing_post.published = post.published
    session.commit()
    session.refresh(existing_post)
        
    post_response = schemas.PostRead.model_validate(existing_post)
    return format_response(post_response, "Post updated successfully")

@router.delete('/{id}', response_model=dict)
async def delete_post(id: int, session: Annotated[Session, Depends(get_session)],current_user: Annotated[schemas.TokenData, Depends(get_current_user)]):
    post = session.exec(select(models.Post).where(models.Post.id == id)).first()

    if not post:
        return format_response(None, "No Post found", status=False)
    

    if post.owner_id != current_user.id:
        return format_response(None, "You are not authorized to perform this action", status=False)
    

    session.delete(post)
    session.commit()
    return format_response(None, "Post deleted successfully")    


