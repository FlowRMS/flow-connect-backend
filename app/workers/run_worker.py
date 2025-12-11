"""Entry point for running the TaskIQ campaign worker."""

import asyncio
import logging
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# How often to check for campaigns (in seconds)
CHECK_INTERVAL = 60  # 1 minute


async def run_scheduler() -> None:
    """Run the campaign processing task on a schedule using TaskIQ."""
    from app.workers.broker import broker
    from app.workers.tasks import check_and_process_campaigns_task

    # Start the broker
    await broker.startup()
    logger.info("TaskIQ broker started")

    try:
        while True:
            logger.info("Scheduling campaign processing task...")
            try:
                # Kick off the task using TaskIQ
                task = await check_and_process_campaigns_task.kiq()
                # Wait for result
                result = await task.wait_result(timeout=300)
                if result.is_err:
                    logger.error(f"Task failed: {result.error}")
                else:
                    logger.info(f"Task completed: {result.return_value}")
            except Exception as e:
                logger.exception(f"Error running campaign task: {e}")

            # Wait before next run
            await asyncio.sleep(CHECK_INTERVAL)
    finally:
        await broker.shutdown()
        logger.info("TaskIQ broker stopped")


async def main() -> None:
    """Main entry point for the worker."""
    logger.info("Starting TaskIQ campaign email worker...")
    await run_scheduler()


if __name__ == "__main__":
    asyncio.run(main())
