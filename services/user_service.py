from datetime import timedelta, timezone, datetime
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError
import jwt
from .schemas import (
    Item_addDB,
    Token,
    UserCreate,
    TokenData,
    buy_form,
    user_base,
    buy_order,
    create_role
)
from db.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import user_table, item_table, order_table
from config import JWT_ALGORITHM, JWT_SECRET, ACCESS_TOKEN_EXPIRE_MINUTES
from passlib.context import CryptContext
from sqlalchemy.exc import *    # noqa: F403
import random
from psycopg2 import IntegrityError


# from api.dependencies import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")







async def get_item(itemname, db: AsyncSession):
    query = item_table.select().where(item_table.c.name == itemname)
    found_item = await db.execute(query)

    found_item = found_item.mappings().first()
    if found_item:
        return found_item
    else:
        return None


async def get_email(email, db: AsyncSession):
    query1 = user_table.select().where(user_table.c.email == email)
    found_user = await db.execute(query1)
    found_user = found_user.mappings().one()

    if found_user:
        return found_user
    else:
        return None


async def get_id(_id, db: AsyncSession):
    query1 = user_table.select().where(user_table.c.id == _id)
    found_user = await db.execute(query1)
    found_user = found_user.mappings().one()
    if found_user:
        return found_user
    else:
        return None


async def create_item(item_name):
    item_cost = random.randint(1, 100)
    item_quantity = random.randint(0, 10)
    return Item_addDB(name=item_name, cost=item_cost, quantity=item_quantity)








async def buy_service(
    item: buy_form,
    user: user_base,
    db: AsyncSession
):
    itemindb = await get_item(item.name, db)
    
    if not itemindb:
        raise BaseException("Такого нету иди нахуй")
    
    if itemindb.quantity < item.quantity:
        raise BaseException("Еблан наличия нет")
    
    finalcost = itemindb.cost * item.quantity

    if user.money < finalcost:
        raise BaseException("Безденежное чмо")
    
    order_create = buy_order(item_id = itemindb.id, quantity=item.quantity, user_id = user.id )

    query = user_table.update().where(user_table.c.id == user.id).values(money = user.money - finalcost)
    query1 = item_table.update().where(item_table.c.id == itemindb.id).values(quantity = itemindb.quantity - item.quantity)
    query2 = order_table.insert().values(**order_create.dict())
    await db.execute(query)
    await db.execute(query1)
    await db.execute(query2)
    await db.commit()
    return order_create




async def service_getuser_by_jwt(jwt_token, db: AsyncSession = Depends(get_async_session)):
    try:
        decoded_jwt = jwt.decode(
            jwt_token,
            JWT_SECRET,
            JWT_ALGORITHM,
        )
        user_id = decoded_jwt["id"]
    except jwt.exceptions.DecodeError:
        return "ПАШЁЛ НАХУЙ ХАКЕР Я ТВАЮ МАМАШУ ЕБАЛ"
    except jwt.exceptions.ExpiredSignatureError:
        return "перелогинься, время вышло"
    except:  # noqa: E722
        return "Ошибка какая-то, бля хз"

    result = await get_id(user_id, db)

    return result

async def service_add_item(item_name, user: user_base, db: AsyncSession = Depends(get_async_session)):
    if not user.is_superuser:
        return "Ну але ты не админ ты лох лох"
    new_item = await create_item(item_name)
    query = item_table.insert().values(**new_item.dict())

    try:
        inserted_item = await db.execute(query)
    except IntegrityError:  # noqa: F405
        return "такой предмет уже есть, ХУЕСОС"

    await db.commit()

    return f"Поздравляем, вы пополнили магазин, добавили {item_name} под id {inserted_item.inserted_primary_key}"

