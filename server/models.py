from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class Member(BaseModel):
    membername: str


class Message(BaseModel):
    text: str
