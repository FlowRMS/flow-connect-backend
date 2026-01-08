import json
import polars as pl
from app.auth.workos_auth_service import WorkOSAuthService
from app.core.config.base_settings import  get_settings_local
from app.core.config.workos_settings import WorkOSSettings


def get_credentials(tenant: str, env: str, role: str) -> tuple[str, str, str | None]:

    df = pl.read_csv("logins-workos.csv")
    df_row = (
        df.filter(pl.col("tenant") == tenant)
        .filter(pl.col("env") == env)
        .filter(pl.col("role") == role)
    )

    if df_row.height == 0:
        raise ValueError(
            f"No credentials found for tenant={tenant}, env={env}, role={role}"
        )

    return df_row[0, "email"], df_row[0, "password"], df_row[0, "organization_id"]


async def generate_token(tenant: str, env: str, role: str) -> str:
    auth_service = WorkOSAuthService(
        workos_settings=get_settings_local(env=env, cls=WorkOSSettings)
    )

    email, password, organization_id = get_credentials(tenant, env, role)
    token = await auth_service.authenticate(
        email=email, password=password, tenant_id=organization_id
    )
    if not token:
        raise ValueError("Failed to generate token")

    return token.access_token


if __name__ == "__main__":
    import asyncio
    import argparse

    parser = argparse.ArgumentParser(description="Generate JWT token for a user")
    _ = parser.add_argument("--tenant", type=str, required=True, help="Tenant name")
    _ = parser.add_argument(
        "--env", type=str, required=False, help="Environment", default="staging"
    )
    _ = parser.add_argument(
        "--role", type=str, required=False, help="User role", default="admin"
    )

    args = parser.parse_args()
    token = asyncio.run(generate_token(args.tenant, args.env, args.role))
    print(
        json.dumps(
            {"Authorization": f"Bearer {token}"}, indent=2
        )
    )