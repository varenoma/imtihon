import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database import async_session
from models.admin import Admin
from auth.utils import hash_password


async def create_admin():
    async with async_session() as db:

        username = input("Admin username: ")
        password = input("Admin password: ")

        result = await db.execute(select(Admin).where(Admin.username == username))
        existing = result.scalar_one_or_none()

        if existing:
            print("Admin already exists.")
            return

        new_admin = Admin(
            username=username,
            hashed_password=hash_password(password)
        )

        db.add(new_admin)
        await db.commit()
        await db.refresh(new_admin)
        print("✅ Admin created successfully.")

if __name__ == "__main__":
    asyncio.run(create_admin())
