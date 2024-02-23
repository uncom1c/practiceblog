from psycopg2 import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
# from datetime import datetime
import datetime
from fastapi import Depends
from api.post.schemas import user_base
from db.database import get_async_session
from .schemas import Post
from db.models import post_table, like_table

async def create_post(post_template, id):
    dt_now = datetime.datetime.now()
    print(dt_now)
    print(datetime.date)
    return Post(title= post_template.title, text= post_template.text, user_id= id, post_date= dt_now )


async def service_add_post(post_template, user: user_base, db: AsyncSession = Depends(get_async_session)):
    
    new_post = await create_post(post_template, user.id)
    query = post_table.insert().values(**new_post.dict())

    try:
        inserted_post = await db.execute(query)
    except IntegrityError:  # noqa: F405
        return "такое название уже есть, ХУЕСОС"

    await db.commit()

    return f"Поздравляем, вы пополнили блог, добавив {post_template.title} под id {inserted_post.inserted_primary_key}"



async def get_post(post_id, db: AsyncSession):
    query = post_table.select().where(post_table.c.id == post_id)
    found_post = await db.execute(query)

    found_post = found_post.mappings().first()
    if found_post:
        return found_post
    else:
        return None
    
async def check_if_liked(template, db: AsyncSession):
    query = like_table.select().where(like_table.c.user_id == template.user_id, like_table.c.post_id == template.post_id)

    found_likes = await db.execute(query)
    found_likes = found_likes.mappings().all()
    if not found_likes:
        return None
    else:
        return "Уже лайкнуто СУКА"
    
    
async def service_like_post(template, db: AsyncSession):
    found_likes = await check_if_liked(template, db)

    if found_likes:
        return found_likes
    else:
        new_like = template
        query = like_table.insert().values(**new_like.dict())
        try:
            inserted_like = await db.execute(query)
        except IntegrityError:  # noqa: F405
            return "ХУЕСОС"

        await db.commit()
        
        return f"Поздравляем, вы лайкнули пост {template}"
        