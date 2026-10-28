from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Users and Posts API",
    description="A typed API with documented inputs, outputs and error responses.",
    version="1.0.0",
)

NOT_FOUND = {404: {"model": schemas.ErrorResponse, "description": "Resource not found"}}


@app.post(
    "/users",
    response_model=schemas.UserRead,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"model": schemas.ErrorResponse, "description": "Username or email already exists"}},
    tags=["users"],
)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(username=payload.username, email=payload.email)
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")
    db.refresh(user)
    return user


@app.get("/users", response_model=List[schemas.UserRead], tags=["users"])
def list_users(db: Session = Depends(get_db)):
    return db.scalars(select(models.User)).all()


@app.get("/users/{user_id}", response_model=schemas.UserWithPosts, responses=NOT_FOUND, tags=["users"])
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, responses=NOT_FOUND, tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()


@app.post(
    "/users/{user_id}/posts",
    response_model=schemas.PostRead,
    status_code=status.HTTP_201_CREATED,
    responses=NOT_FOUND,
    tags=["posts"],
)
def create_post(user_id: int, payload: schemas.PostCreate, db: Session = Depends(get_db)):
    if db.get(models.User, user_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    post = models.Post(title=payload.title, content=payload.content, user_id=user_id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@app.get("/posts", response_model=List[schemas.PostRead], tags=["posts"])
def list_posts(db: Session = Depends(get_db)):
    return db.scalars(select(models.Post)).all()
