import aiosqlite

DB_NAME = "casino.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0
        )
        """)
        await db.commit()

async def get_balance(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return row[0] if row else 0

async def add_balance(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO users(user_id, balance)
        VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET balance = balance + ?
        """, (user_id, amount, amount))
        await db.commit()

async def remove_balance(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        await db.commit()
