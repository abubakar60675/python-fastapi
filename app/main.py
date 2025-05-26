from fastapi import FastAPI, Depends, HTTPException, Request
from sqlmodel import SQLModel, create_engine, Session, select
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

from .routes import user, post, auth, vote

from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]



@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Creating Tables')
    create_tables()
    print("Tables Created")
    yield

app = FastAPI(
    lifespan=lifespan, title="Posts App", version='1.0.0'
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=format_response(None, exc.detail, status=False)
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    
    # Extract field names from errors
    fields = []
    for err in errors:
        loc = err.get("loc", [])
        if len(loc) >= 2 and loc[0] == "body":
            fields.append(loc[1])
    fields = sorted(set(fields))
    
    if fields:
        message = f"Missing or invalid fields: {', '.join(fields)}"
    else:
        message = "Validation error"
    
    return JSONResponse(
        status_code=422,
        content=format_response(
            data=errors,
            message=message,
            status=False
        ),
    )



app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)

@app.get('/')
async def root():
    return {"message": "Welcome to FastAPI"}



