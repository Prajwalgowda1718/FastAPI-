from pydantic import BaseModel

class PostCreate(BaseModel):
    name:str
    title:str
    content:str

class PostReturn(BaseModel):
    name:str
    title:str
    content:str