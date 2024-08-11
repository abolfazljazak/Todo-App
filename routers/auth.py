from fastapi import APIRouter
from pydantic import BaseModel
from passlib.context import CryptContext

from models import Users

router = APIRouter()


bcrypt_context = CryptContext(schemes='bcrypt', deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str
    role: str


@router.post("/auth/")
async def get_user(create_user_request: CreateUserRequest):

    user = Users(
        username=create_user_request.username,
        hash_password=bcrypt_context.hash(create_user_request.password),
        email=create_user_request.email,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
    )
    return user
