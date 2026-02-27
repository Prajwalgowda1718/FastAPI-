from pydantic import BaseModel
from fastapi_users import schemas
import uuid

class UserRead(schemas.BaseUser[uuid.UUID]):
    pass

class UserCreate(schemas.BaseUserCreate):
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass

class PostCreate(BaseModel):
    name:str
    title:str
    content:str

class PostReturn(BaseModel):
    name:str
    title:str
    content:str