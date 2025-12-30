from workos import AsyncWorkOSClient
from app.core.config.workos_settings import WorkOSSettings
from app.core.config.base_settings import get_settings

settings = get_settings(WorkOSSettings)



client = AsyncWorkOSClient(
        api_key=settings.workos_api_key,
        client_id=settings.workos_client_id,
    )

async def main():
    _ = await client.user_management.update_user(
        user_id="user_01KDHXAD5GKKQ0AEMQJ8GVJX4J",
        first_name="Juan",
        last_name="Pablo",
        external_id="be15c0e9-1cfb-4bef-a0b3-e14b35042874",
    )
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())