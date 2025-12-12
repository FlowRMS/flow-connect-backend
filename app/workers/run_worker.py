"""Entry point for running the TaskIQ campaign worker and scheduler."""

import asyncio

from loguru import logger
from taskiq.api.scheduler import run_scheduler_task


async def run_all() -> None:
    """
    Run both scheduler and worker together.

    Uses TaskIQ's run_scheduler_task which handles the cron loop properly.
    With RedisStreamBroker, tasks can be distributed across multiple workers.
    """
    # Import tasks to register them with the broker
    from app.workers import tasks as _tasks  # noqa: F401
    from app.workers.broker import broker, scheduler

    del _tasks  # Silence unused import warning

    logger.info("Starting TaskIQ broker...")
    await broker.startup()
    logger.info("TaskIQ broker started")

    logger.info("Starting TaskIQ scheduler with cron schedule...")
    try:
        # run_scheduler_task handles the scheduler loop and cron checking
        await run_scheduler_task(scheduler, run_startup=False)
    except asyncio.CancelledError:
        logger.info("Shutting down...")
    finally:
        await scheduler.shutdown()
        await broker.shutdown()
        logger.info("TaskIQ broker and scheduler stopped")


async def main() -> None:
    """Main entry point for the worker."""
    logger.info("Starting TaskIQ campaign email worker...")
    await run_all()


if __name__ == "__main__":
    asyncio.run(main())
