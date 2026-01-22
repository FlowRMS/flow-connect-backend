import argparse
import asyncio
from pathlib import Path

from commons.db.models.tenant import Tenant
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from workos import AsyncWorkOSClient


class ScriptSettings(BaseSettings):
    workos_api_key: str
    workos_client_id: str
    pg_url: str

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


def load_settings(env: str) -> ScriptSettings:
    env_file = get_env_file(env)
    env_path = Path(__file__).parent.parent / env_file
    if not env_path.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    return ScriptSettings(_env_file=str(env_path))


async def get_tenants(pg_url: str) -> list[Tenant]:
    engine = create_async_engine(pg_url)
    try:
        async with AsyncSession(engine) as session:
            stmt = select(Tenant).order_by(Tenant.name)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    finally:
        await engine.dispose()


async def update_org_external_id(
    client: AsyncWorkOSClient,
    org_id: str,
    external_id: str,
    dry_run: bool,
) -> bool:
    if dry_run:
        print(f"  [DRY RUN] Would update external_id to: {external_id}")
        return True

    try:
        _ = await client.organizations.update_organization(
            organization_id=org_id,
            external_id=external_id,
        )
        print(f"  Updated external_id to: {external_id}")
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
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

    tenants = await get_tenants(settings.pg_url)
    print(f"Found {len(tenants)} tenant(s)")
    print()

    success_count = 0
    skip_count = 0
    error_count = 0

    for tenant in tenants:
        print(f"Tenant: {tenant.name}")
        print(f"  ID: {tenant.id}")
        print(f"  WorkOS Org ID: {tenant.org_id}")

        if not tenant.org_id:
            print("  SKIPPED: No WorkOS org_id configured")
            skip_count += 1
            continue

        org = await client.organizations.get_organization(organization_id=tenant.org_id)
        print(f"  Current external_id: {org.external_id}")

        if org.external_id == str(tenant.id):
            print("  SKIPPED: external_id already matches tenant ID")
            skip_count += 1
            continue

        if await update_org_external_id(client, tenant.org_id, str(tenant.id), dry_run):
            success_count += 1
        else:
            error_count += 1

        print()

    print("=" * 60)
    print(f"Results: {success_count} updated, {skip_count} skipped, {error_count} errors")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update WorkOS organization external_ids to match tenant IDs"
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
        help="Show what would be updated without making changes",
    )

    args = parser.parse_args()
    asyncio.run(main(args.env, args.dry_run))
