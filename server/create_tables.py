def create_tables(con):
    cur = con.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
    );
    ''')
    con.commit()

    cur = con.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS chats (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    member_id1 INTEGER NOT NULL,
    member_id2 INTEGER NOT NULL
    );
    ''')
    con.commit()

    cur = con.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS messages (
    id INTEGER NOT NULL UNIQUE PRIMARY KEY,
    user_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    date TIMESTAMP NOT NULL
    );
    ''')
    con.commit()
