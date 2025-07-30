import asyncio
import csv

from pqapi import async_add_user
from pqapi.models import UserModel


def read_csv(file_path: str) -> list[UserModel]:
    with open(file_path, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return [UserModel(email=r["email"], full_name=r["full_name"]) for r in reader]


async def upload_users(users: list[UserModel]) -> None:
    tasks = [async_add_user(user) for user in users]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(f"Successfully uploaded {len(results)} users")


async def main(file_path: str):
    users = read_csv(file_path)
    await upload_users(users)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:  # noqa: PLR2004
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)

    csv_file_path = sys.argv[1]
    asyncio.run(main(csv_file_path))
