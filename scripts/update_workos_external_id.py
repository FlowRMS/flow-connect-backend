"""
Update a user's external_id in WorkOS.

Usage:
    uv run python scripts/update_workos_external_id.py <env> <workos_user_id> <new_external_id>

Arguments:
    env             - Environment: local, staging, or production
    workos_user_id  - WorkOS user ID (e.g., user_01ABC123...)
    new_external_id - New external ID (UUID format)

Examples:
    uv run python scripts/update_workos_external_id.py staging user_01ABC123 550e8400-e29b-41d4-a716-446655440000
    uv run python scripts/update_workos_external_id.py production user_01XYZ789 123e4567-e89b-12d3-a456-426614174000
"""

import argparse
import asyncio
import uuid
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from workos import AsyncWorkOSClient


class EnvWorkOSSettings(BaseSettings):
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
        raise ValueError(f"Invalid environment: {env}. Must be one of: {list(env_files.keys())}")
    return env_files[env]


def load_settings(env: str) -> EnvWorkOSSettings:
    env_file = get_env_file(env)
    env_path = Path(__file__).parent.parent / env_file

    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")

    return EnvWorkOSSettings(_env_file=str(env_path))


async def update_external_id(
    settings: EnvWorkOSSettings,
    user_id: str,
    new_external_id: uuid.UUID,
) -> None:
    client = AsyncWorkOSClient(
        api_key=settings.workos_api_key,
        client_id=settings.workos_client_id,
    )

    print(f"Fetching user {user_id}...")
    current_user = await client.user_management.get_user(user_id=user_id)
    print(f"  Email: {current_user.email}")
    print(f"  Name: {current_user.first_name} {current_user.last_name}")
    print(f"  Current external_id: {current_user.external_id}")

    print(f"\nUpdating external_id to: {new_external_id}")
    updated_user = await client.user_management.update_user(
        user_id=user_id,
        external_id=str(new_external_id),
    )
    print(f"  New external_id: {updated_user.external_id}")
    print("\nUpdate successful!")


def main() -> None:
    parser = argparse.ArgumentParser(description="Update a user's external_id in WorkOS")
    parser.add_argument("env", choices=["local", "staging", "production"], help="Environment")
    parser.add_argument("user_id", help="WorkOS user ID (e.g., user_01ABC123)")
    parser.add_argument("external_id", help="New external ID (UUID format)")

    args = parser.parse_args()

    try:
        new_external_id = uuid.UUID(args.external_id)
    except ValueError:
        print(f"Error: Invalid UUID format: {args.external_id}")
        return

    if not args.user_id.startswith("user_"):
        print(f"Warning: WorkOS user IDs typically start with 'user_'. Got: {args.user_id}")

    print(f"Environment: {args.env}")
    print(f"User ID: {args.user_id}")
    print(f"New External ID: {new_external_id}")
    print("=" * 60)

    settings = load_settings(args.env)
    asyncio.run(update_external_id(settings, args.user_id, new_external_id))


if __name__ == "__main__":
    main()
