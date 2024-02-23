from pydantic import BaseModel, EmailStr
from datetime import datetime

class Post(BaseModel):
    title: str
    text: str
    user_id: int
    post_date: datetime

class Create_Post(BaseModel):
    title: str
    text: str

class user_base(BaseModel):
    id: int
    email: EmailStr
    username: str

class LikedPost(BaseModel):
    user_id: int
    post_id: int