"""Entry point for running the campaign email worker."""

import asyncio
import logging
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.workers.campaign_worker import check_and_process_campaigns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# How often to check for campaigns (in seconds)
CHECK_INTERVAL = 60  # 1 minute


async def run_periodic_check() -> None:
    """Run the campaign check periodically."""
    logger.info("Starting periodic campaign processor...")

    while True:
        try:
            logger.info("Checking for campaigns to process...")
            result = await check_and_process_campaigns()
            logger.info(f"Campaign check result: {result}")
        except Exception as e:
            logger.exception(f"Error in periodic campaign check: {e}")

        await asyncio.sleep(CHECK_INTERVAL)


async def main() -> None:
    """Main entry point for the worker."""
    logger.info("Starting campaign email worker...")
    await run_periodic_check()


if __name__ == "__main__":
    asyncio.run(main())
