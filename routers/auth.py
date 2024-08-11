from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordRequestForm, OAuth2PasswordBearer
)

from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import Users

from jose import (
    jwt,
    JWTError
)

SECRET_KEY = "eyJzdWIiOiJqb2huX2RvZSIsImlkIjo0Mn0"
ALGORITHM = "HS256"


router = APIRouter()


bcrypt_context = CryptContext(schemes='bcrypt', deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def get_user(db: db_dependency, create_user_request: CreateUserRequest):

    user = Users(
        username=create_user_request.username,
        hash_password=bcrypt_context.hash(create_user_request.password),
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
    )

    db.add(user)
    db.commit()


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hash_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.utcnow() + expire_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm="HS256")


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        pyload = jwt.decode(token, SECRET_KEY, [ALGORITHM])
        username: str = pyload.get('username')
        user_id: int = pyload.get('user_id')
        if username is None or user_id is None:
            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validate user."
                                )
        return {"username": username, "user_id": user_id}

    except JWTError:
        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validate user."
                            )


@router.post("/token", response_model=Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return "Failed Authentication"

    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {"access_token": token, "token_type": 'bearer'}
