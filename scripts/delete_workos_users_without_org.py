import argparse
import asyncio
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from workos import AsyncWorkOSClient


class ScriptSettings(BaseSettings):
    workos_api_key: str
    workos_client_id: str

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_env_file(env: str) -> str:
    env_files = {
        "local": ".env.local",
        "staging": ".env.staging",
        "production": ".env.production",
    }
    if env not in env_files:
        raise ValueError(
            f"Invalid environment: {env}. Must be one of: {list(env_files.keys())}"
        )
    return env_files[env]


def load_settings(env: str) -> ScriptSettings:
    env_file = get_env_file(env)
    env_path = Path(__file__).parent.parent / env_file
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    return ScriptSettings(_env_file=str(env_path))


async def get_all_users(client: AsyncWorkOSClient) -> list[dict]:
    users = []
    after: str | None = None

    while True:
        response = await client.user_management.list_users(limit=100, after=after)
        for user in response.data:
            users.append({
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": user.created_at,
            })

        if not response.list_metadata.after:
            break
        after = response.list_metadata.after

    return users


async def get_user_org_count(client: AsyncWorkOSClient, user_id: str) -> int:
    response = await client.user_management.list_organization_memberships(
        user_id=user_id, limit=1
    )
    return len(response.data)


async def delete_user(
    client: AsyncWorkOSClient,
    user_id: str,
    dry_run: bool,
) -> bool:
    if dry_run:
        print(f"  [DRY RUN] Would delete user")
        return True

    try:
        await client.user_management.delete_user(user_id)
        print(f"  Deleted user")
        return True
    except Exception as e:
        print(f"  ERROR deleting user: {e}")
        return False


async def main(env: str, dry_run: bool) -> None:
    settings = load_settings(env)

    client = AsyncWorkOSClient(
        api_key=settings.workos_api_key,
        client_id=settings.workos_client_id,
    )

    print(f"Environment: {env}")
    print(f"Dry run: {dry_run}")
    print("=" * 60)

    print("Fetching all users from WorkOS...")
    users = await get_all_users(client)
    print(f"Found {len(users)} total user(s)")
    print()

    users_without_org = []

    print("Checking organization memberships...")
    for i, user in enumerate(users, 1):
        org_count = await get_user_org_count(client, user["id"])
        if org_count == 0:
            users_without_org.append(user)
        if i % 50 == 0:
            print(f"  Checked {i}/{len(users)} users...")

    print()
    print(f"Found {len(users_without_org)} user(s) without any organization")
    print("=" * 60)

    if not users_without_org:
        print("No users to delete.")
        return

    delete_count = 0
    error_count = 0

    for user in users_without_org:
        print(f"User: {user['email']}")
        print(f"  ID: {user['id']}")
        print(f"  Name: {user['first_name']} {user['last_name']}")
        print(f"  Created: {user['created_at']}")

        if await delete_user(client, user["id"], dry_run):
            delete_count += 1
        else:
            error_count += 1

        print()

    print("=" * 60)
    print(f"Results: {delete_count} deleted, {error_count} errors")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Delete WorkOS users that have no organization memberships"
    )
    _ = parser.add_argument(
        "--env",
        choices=["local", "staging", "production"],
        required=True,
        help="Environment to run against",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without making changes",
    )

    args = parser.parse_args()
    asyncio.run(main(args.env, args.dry_run))
