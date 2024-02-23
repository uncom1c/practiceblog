from datetime import timedelta, timezone, datetime
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from .schemas import (
    Token,
    UserCreate
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table, like_table
from config import JWT_ALGORITHM, JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from sqlalchemy.exc import *    # noqa: F403


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_username(username, db: AsyncSession):
    query = user_table.select().where(user_table.c.username == username)
    found_user = await db.execute(query)

    found_user = found_user.mappings().first()
    if found_user:
        return found_user
    else:
        return None


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)



def encode_user(user: UserCreate):
    return UserCreate(
        email=user.email,
        username=user.username,
        password=get_password_hash(user.password),
    )



async def service_register_handler(
    user_create: UserCreate, db: AsyncSession = Depends(get_async_session)
):
    print(user_create)
    user_create = encode_user(user_create)
    query = user_table.insert().values(**user_create.dict())

    try:
        inserted_user = await db.execute(query)
    except:
        return "такой пользователь уже есть, ХУЕСОС"

    await db.commit()
    # print(await assign_role())
    
    
    return (
        f"Поздравляем, вы зарегались, пользователь {inserted_user.inserted_primary_key}"
    )


async def service_login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_async_session),
) -> Token:
    result = await get_username(form_data.username, db)

    if not result:
        return "no such user"

    if not verify_password(form_data.password, result["password"]):
        return "wrong password"

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": result["username"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

async def user_liked_posts(id, db: AsyncSession):
    query = like_table.select().where(like_table.c.user_id == id)
    found_likes = await db.execute(query)

    found_likes = found_likes.mappings().all()
    liked_id = []
    for i in range(len(found_likes)):
        liked_id.append(found_likes[i].post_id)
    if found_likes:
        return liked_id
    else:
        return None
