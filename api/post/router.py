from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from api.auth.router import get_current_user
from api.post.service import service_add_post, service_like_post


from .schemas import (
    Create_Post,
    LikedPost,
    Post,
    user_base
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import post_table, like_table


router = APIRouter()


@router.post("/post")
async def add_post(post_template: Create_Post, user: Annotated[user_base, Depends(get_current_user)], db: AsyncSession = Depends(get_async_session)):
    try:
        posted = await service_add_post(post_template, user, db)
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )


    return posted

@router.get("/all")
async def all_handler(db: AsyncSession = Depends(get_async_session)):
    query = post_table.select()
    result = await db.execute(query)

    return result.mappings().all()

@router.get("/all_likes")
async def all_likes_handler(db: AsyncSession = Depends(get_async_session)):
    query = like_table.select()
    result = await db.execute(query)

    return result.mappings().all()

@router.post("/like")
async def like_handler(user: Annotated[user_base, Depends(get_current_user)], post_id, db: AsyncSession = Depends(get_async_session)):
    template = LikedPost(user_id = user.id, post_id= post_id)
    try:
        liked = await service_like_post(template, db)
        return liked
    except BaseException as _ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=_ex
        )


    return "Лайк поставлен сука"
