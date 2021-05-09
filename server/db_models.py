import ormar
from server import metadata, database


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Users(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'users'
    id: int = ormar.Integer(primary_key=True, unique=True, nullable=False)
    username: str = ormar.Text(unique=True, nullable=False)
    password: str = ormar.Text(nullable=False)


class Chats(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'chats'
    id: int = ormar.Integer(primary_key=True, unique=True, nullable=False)
    member_id1: int = ormar.Integer(nullable=False)
    member_id2: int = ormar.Integer(nullable=False)


class Messages(ormar.Model):
    class Meta(BaseMeta):
        tablename = 'messages'
    id: int = ormar.Integer(primary_key=True, unique=True, nullable=False)
    user_id: int = ormar.Integer(nullable=False)
    chat_id: int = ormar.Integer(nullable=False)
    message_text: str = ormar.Text(nullable=False)
    date: str = ormar.DateTime(nullable=False)


# def create_tables(con):
#     cur = con.cursor()
#     cur.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#     id INTEGER NOT NULL UNIQUE PRIMARY KEY,
#     username TEXT UNIQUE NOT NULL,
#     password TEXT NOT NULL
#     );
#     ''')
#     con.commit()
#
#     cur = con.cursor()
#     cur.execute('''
#     CREATE TABLE IF NOT EXISTS chats (
#     id INTEGER NOT NULL UNIQUE PRIMARY KEY,
#     member_id1 INTEGER NOT NULL,
#     member_id2 INTEGER NOT NULL
#     );
#     ''')
#     con.commit()
#
#     cur = con.cursor()
#     cur.execute('''
#     CREATE TABLE IF NOT EXISTS messages (
#     id INTEGER NOT NULL UNIQUE PRIMARY KEY,
#     user_id INTEGER NOT NULL,
#     chat_id INTEGER NOT NULL,
#     message_text TEXT NOT NULL,
#     date TIMESTAMP NOT NULL
#     );
#     ''')
#     con.commit()
