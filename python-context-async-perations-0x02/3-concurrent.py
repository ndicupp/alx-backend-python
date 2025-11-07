I'm going to run multiple SQLite queries concurrently, we can use aiosqlite and asyncio.gather. Here’s a complete example:
import asyncio
import aiosqlite

# Asynchronous function to fetch all users
async def async_fetch_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            return results

# Asynchronous function to fetch users older than 40
async def async_fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            return results

# Function to run both queries concurrently
async def fetch_concurrently():
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    print("All users:", all_users)
    print("Users older than 40:", older_users)

# Run the concurrent fetch
asyncio.run(fetch_concurrently())

How it works:

async_fetch_users and async_fetch_older_users are async functions that open the database asynchronously and fetch results.

asyncio.gather runs them concurrently, so both queries can execute at the same time.

asyncio.run starts the asynchronous event loop and runs the fetch_concurrently coroutine.
