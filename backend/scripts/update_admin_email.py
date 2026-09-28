"""One-off script: updates the existing 'admin' user's username to a real
email address, so Forgot Password can be tested against that account.

Run once from the backend folder with the venv active:
    python scripts/update_admin_email.py

Safe to delete after running.
"""

import asyncio
import sys
from pathlib import Path

# Make sure the backend folder (this script's parent) is on sys.path,
# so `app.*` imports resolve regardless of how this script is invoked
# (running "python scripts/update_admin_email.py" puts scripts/ on
# sys.path, not backend/ — this fixes that).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.modules.auth.models import User

OLD_USERNAME = "admin"
NEW_USERNAME = "athithyag24@gmail.com"


async def main() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == OLD_USERNAME))
        user = result.scalar_one_or_none()
        if user is None:
            print(f"No user found with username '{OLD_USERNAME}' — nothing to update.")
            return

        existing = await db.execute(select(User).where(User.username == NEW_USERNAME))
        if existing.scalar_one_or_none() is not None:
            print(f"A user with username '{NEW_USERNAME}' already exists — aborting.")
            return

        user.username = NEW_USERNAME
        await db.commit()
        print(f"Updated: '{OLD_USERNAME}' -> '{NEW_USERNAME}'. Log in with the new email from now on.")


if __name__ == "__main__":
    asyncio.run(main())
