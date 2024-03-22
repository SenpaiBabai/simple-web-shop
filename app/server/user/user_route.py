from fastapi import APIRouter, Depends, Body

from starlette import status

from app.server.schemas import UserModel, UserCollections
from app.server.user.user_db import User

router = APIRouter(
    prefix="/users",
    tags=["user"],
)


@router.get(
    "/",
    description='Endpoint that show all users',
    response_description="List all users",
    response_model=UserCollections,
    response_model_by_alias=False,
)
async def list_users():
    return UserCollections(users=await User.get_all_users())


@router.post(
    "/",
    description='Endpoint that adds a new user',
    response_description="New user",
    response_model=UserModel,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_user(user: UserModel = Body()):
    new_user = await User.create_user(user)
    return new_user


@router.delete("/{user_id}", description="Endpoint which removes user")
async def delete_user(user_id: str):
    delete_result = await User.delete_user(user_id)
    return delete_result
