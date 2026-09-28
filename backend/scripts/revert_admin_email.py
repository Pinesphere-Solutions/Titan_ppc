"""One-off script: reverts the admin user's username back to 'admin'
(undoes update_admin_email.py). Run once from the backend folder with
the venv active:
    python scripts/revert_admin_email.py

Safe to delete after running.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.modules.auth.models import User

CURRENT_USERNAME = "athithyag24@gmail.com"
REVERT_TO_USERNAME = "admin"


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == CURRENT_USERNAME))
        user = result.scalar_one_or_none()
        if user is None:
            print(f"No user found with username '{CURRENT_USERNAME}' — nothing to revert.")
            return

        existing = await db.execute(select(User).where(User.username == REVERT_TO_USERNAME))
        if existing.scalar_one_or_none() is not None:
            print(f"A user with username '{REVERT_TO_USERNAME}' already exists — aborting.")
            return

        user.username = REVERT_TO_USERNAME
        await db.commit()
        print(f"Reverted: '{CURRENT_USERNAME}' -> '{REVERT_TO_USERNAME}'. Log in with '{REVERT_TO_USERNAME}' again.")


if __name__ == "__main__":
    asyncio.run(main())
