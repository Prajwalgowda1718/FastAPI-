# app/users.py
import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db import User, get_user_db
from dotenv import load_dotenv
import os

load_dotenv()

SECRET = os.getenv("SECRET_KEY")

# 1. User Manager ───────────
class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    # Hook into lifecycle events
    async def on_after_register(self, user: User, request=None):
        print(f"User {user.email} has registered.")

    async def on_after_forgot_password(self, user, token, request=None):
        print(f"Password reset requested for {user.email}")

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# 2. JWT Transport & Strategy ────────
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=3600   # Token valid for 1 hour
    )

# 3. Authentication Backend 
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# ── 4. FastAPIUsers Instance ─────
fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# ── 5. Dependency: get current logged-in user ─────────
current_active_user = fastapi_users.current_user(active=True)