"""Database index definitions."""


async def ensure_indexes(database):
    await database["users"].create_index("email", unique=True)
