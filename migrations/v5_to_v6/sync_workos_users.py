import asyncio
import logging
import uuid
from dataclasses import dataclass

from commons.db.controller import MultiTenantController
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User
from sqlalchemy import select
from workos import AsyncWorkOSClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class SyncConfig:
    pg_url: str
    tenant_url: str
    workos_api_key: str
    workos_client_id: str
    dry_run: bool = False


@dataclass
class SyncResult:
    errors: list[str]
    total_users: int = 0
    users_found_in_workos: int = 0
    users_created_in_workos: int = 0
    users_updated: int = 0
    users_skipped: int = 0

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


async def get_workos_org_id(
    client: AsyncWorkOSClient, tenant_name: str
) -> str | None:
    orgs = await client.organizations.list_organizations()
    for org in orgs.data:
        if org.name == tenant_name:
            return org.id
    return None


async def find_workos_user_by_email(
    client: AsyncWorkOSClient, email: str
) -> tuple[str, uuid.UUID | None] | None:
    users = await client.user_management.list_users(email=email, limit=1)
    if users.data:
        workos_user = users.data[0]
        external_id = (
            uuid.UUID(workos_user.external_id) if workos_user.external_id else None
        )
        return (workos_user.id, external_id)
    return None


async def create_workos_user(
    client: AsyncWorkOSClient,
    user: User,
    org_id: str,
) -> tuple[str, uuid.UUID] | None:
    try:
        workos_user = await client.user_management.create_user(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            email_verified=True,
            external_id=str(user.id),
        )
        _ = await client.user_management.create_organization_membership(
            user_id=workos_user.id,
            organization_id=org_id,
            role_slug=user.role.name.lower(),
        )
        return (workos_user.id, user.id)
    except Exception as e:
        logger.error(f"Failed to create WorkOS user for {user.email}: {e}")
        return None


async def link_existing_user_to_org(
    client: AsyncWorkOSClient,
    workos_user_id: str,
    org_id: str,
    role: RbacRoleEnum,
) -> bool:
    try:
        memberships = await client.user_management.list_organization_memberships(
            user_id=workos_user_id, organization_id=org_id, limit=1
        )
        if memberships.data:
            logger.info(f"User {workos_user_id} already in org {org_id}")
            return True
        _ = await client.user_management.create_organization_membership(
            user_id=workos_user_id,
            organization_id=org_id,
            role_slug=role.name.lower(),
        )
        return True
    except Exception as e:
        logger.error(f"Failed to link user {workos_user_id} to org: {e}")
        return False


async def sync_users_for_tenant(config: SyncConfig) -> SyncResult:
    result = SyncResult(errors=[])
    client = AsyncWorkOSClient(
        api_key=config.workos_api_key,
        client_id=config.workos_client_id,
    )
    controller = MultiTenantController(
        pg_url=config.pg_url,
        app_name="WorkOS User Sync",
        echo=False,
        connect_args={"timeout": 5, "command_timeout": 90},
        env="production",
    )
    await controller.load_data_sources()

    try:
        org_id = await get_workos_org_id(client, config.tenant_url)
        if not org_id:
            result.errors.append(f"WorkOS org not found for tenant: {config.tenant_url}")
            return result

        logger.info(f"Found WorkOS org {org_id} for tenant {config.tenant_url}")

        async with controller.scoped_session(config.tenant_url) as session:
            stmt = select(User).order_by(User.email).where(
                ~User.email.ilike("%@flowrms.com")
            )
            db_result = await session.execute(stmt)
            users = list(db_result.scalars().all())
            result.total_users = len(users)
            logger.info(f"Found {len(users)} users in tenant database")

            for user in users:
                try:
                    await _sync_single_user(
                        client, session, user, org_id, config.dry_run, result
                    )
                except Exception as e:
                    logger.error(f"Error syncing user {user.email}: {e}")
                    result.errors.append(f"{user.email}: {e}")

            if not config.dry_run:
                await session.commit()
    finally:
        pass

    return result


async def _sync_single_user(
    client: AsyncWorkOSClient,
    session: object,
    user: User,
    org_id: str,
    dry_run: bool,
    result: SyncResult,
) -> None:
    # if user.auth_provider_id:
    #     logger.debug(f"User {user.email} already has auth_provider_id, skipping")
    #     result.users_skipped += 1
    #     return

    workos_user = await find_workos_user_by_email(client, user.email)

    if workos_user:
        workos_user_id, external_id = workos_user
        logger.info(f"Found existing WorkOS user for {user.email}: {workos_user_id}")
        result.users_found_in_workos += 1

        linked = await link_existing_user_to_org(
            client, workos_user_id, org_id, user.role
        )
        if not linked:
            result.errors.append(f"Failed to link {user.email} to org")
            return

        if not dry_run:
            user.auth_provider_id = workos_user_id
            result.users_updated += 1
            logger.info(f"Updated auth_provider_id for {user.email}")
            
        if not external_id or external_id != user.id:
            logger.warning(
                f"WorkOS user {user.email} has mismatched external_id "
                f"({external_id} != {user.id})"
            )
            _ = await client.user_management.update_user(
                user_id=workos_user_id,
                external_id=str(user.id),
            )
    else:
        logger.info(f"Creating new WorkOS user for {user.email}")

        if dry_run:
            logger.info(f"[DRY RUN] Would create WorkOS user for {user.email}")
            return

        created = await create_workos_user(client, user, org_id)
        if created:
            workos_user_id, _ = created
            user.auth_provider_id = workos_user_id
            result.users_created_in_workos += 1
            result.users_updated += 1
            logger.info(f"Created WorkOS user and updated {user.email}")
        else:
            result.errors.append(f"Failed to create WorkOS user: {user.email}")


async def run_sync(config: SyncConfig) -> SyncResult:
    logger.info(f"Starting WorkOS user sync for tenant: {config.tenant_url}")
    if config.dry_run:
        logger.info("DRY RUN MODE - no changes will be made")

    result = await sync_users_for_tenant(config)

    logger.info("=" * 60)
    logger.info("Sync Results:")
    logger.info(f"  Total users: {result.total_users}")
    logger.info(f"  Found in WorkOS: {result.users_found_in_workos}")
    logger.info(f"  Created in WorkOS: {result.users_created_in_workos}")
    logger.info(f"  Updated in DB: {result.users_updated}")
    logger.info(f"  Skipped (already synced): {result.users_skipped}")
    if result.errors:
        logger.warning(f"  Errors: {len(result.errors)}")
        for error in result.errors:
            logger.warning(f"    - {error}")
    logger.info("=" * 60)

    return result


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Sync users with WorkOS")
    _ = parser.add_argument("--tenant", required=True, help="Tenant URL to sync")
    _ = parser.add_argument(
        "--pg-url",
        default=os.environ.get("V6_DATABASE_URL"),
        help="PostgreSQL connection URL (base, without tenant)",
    )
    _ = parser.add_argument(
        "--workos-api-key",
        default=os.environ.get("WORKOS_API_KEY"),
        help="WorkOS API key",
    )
    _ = parser.add_argument(
        "--workos-client-id",
        default=os.environ.get("WORKOS_CLIENT_ID"),
        help="WorkOS client ID",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes",
    )
    args = parser.parse_args()

    if not args.pg_url:
        parser.error("--pg-url is required (or set V6_DATABASE_URL)")
    if not args.workos_api_key:
        parser.error("--workos-api-key is required (or set WORKOS_API_KEY)")
    if not args.workos_client_id:
        parser.error("--workos-client-id is required (or set WORKOS_CLIENT_ID)")

    config = SyncConfig(
        pg_url=args.pg_url,
        tenant_url=args.tenant,
        workos_api_key=args.workos_api_key,
        workos_client_id=args.workos_client_id,
        dry_run=args.dry_run,
    )

    _ = asyncio.run(run_sync(config))
