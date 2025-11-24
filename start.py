import os
import uvicorn
import multiprocessing


def get_workers() -> int:
    cores = multiprocessing.cpu_count()
    max_workers = int(os.getenv("MAX_NUMBER_OF_WORKERS", "4"))
    return min((2 * cores) + 1, max_workers)


def main() -> None:
    """Run the FastAPI application with Uvicorn."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5555"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    workers = get_workers()

    # Timeout settings
    timeout_keepalive = int(os.getenv("KEEP_ALIVE", "5"))
    timeout_graceful_shutdown = int(os.getenv("GRACEFUL_TIMEOUT", "120"))

    # Access log configuration
    access_log_var = os.getenv("ACCESS_LOG", "-")
    use_access_log = access_log_var != "none"

    print(f"🚀 Starting on {host}:{port} with {workers} workers")

    uvicorn.run(
        "app.api.app:create_app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        factory=True,
        # Access log configuration
        access_log=use_access_log,
        # Timeout settings
        timeout_keep_alive=timeout_keepalive,
        timeout_graceful_shutdown=timeout_graceful_shutdown,
        # Proxy headers
        proxy_headers=True,
        forwarded_allow_ips="*",
        # Performance settings for production
        loop="asyncio",
        http="httptools",
    )


if __name__ == "__main__":
    main()
