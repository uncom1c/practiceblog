from sqlalchemy import DateTime, Integer, String, ForeignKey, Table, Column, Boolean


from .base import metadata



like_table = Table(
    "likes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user.id"), index=True ,nullable=False),
    Column("post_id", Integer, ForeignKey("post.id"), nullable=False),
    
)

# roles_table = Table(
#     "roles",
#     metadata,
#     Column("id", Integer, ForeignKey("user.id"), index=True, primary_key=True),
#     Column("superuser", Boolean, nullable=False),
    
# )

post_table = Table(
    "post",
    metadata,
    Column("id", Integer, index= True, primary_key=True),
    Column("title", String, index=True, unique=True , nullable=False),
    Column("text", String, nullable=False),
    Column("user_id", Integer, ForeignKey("user.id"), index=True, nullable=False),
    Column("post_date", DateTime, nullable=False),
)

user_table = Table(
    "user",
    metadata,
    Column("id", Integer, index=True, primary_key=True),
    Column("email", String, unique=True, nullable=False),
    Column("username", String, index=True, unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("is_superuser", Boolean, default=0)
)

# class UserManager():
#     reset_password_token_secret = SECRET
#     verification_token_secret = SECRET

#     async def on_after_register(self, user: user, request: Optional[Request] = None):
#         print(f"User {user.id} has registered.")

#     def start(self, request =Request ):
#         self.request: Request = request
#         self.errors: List = []
#         self.username: Optional[str] = None
#         self.email: Optional[str] = None
#         self.password: Optional[str] = None
    
#     async def getting_data(self):
#         form = self.request.form

#     async def validation(self):