import os
import sys
import uvicorn
import multiprocessing


def get_workers() -> int:
    cores = multiprocessing.cpu_count()
    max_workers = int(os.getenv("MAX_NUMBER_OF_WORKERS", "5"))
    return min((2 * cores) + 1, max_workers)


def main() -> None:
    """Run the FastAPI application with Uvicorn."""
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5555"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    
    # On Windows, use single worker for development
    if sys.platform == "win32":
        workers = 1
    else:
        workers = get_workers()

    # Timeout settings
    timeout_keepalive = int(os.getenv("KEEP_ALIVE", "5"))
    timeout_graceful_shutdown = int(os.getenv("GRACEFUL_TIMEOUT", "120"))

    # Access log configuration
    access_log_var = os.getenv("ACCESS_LOG", "-")
    use_access_log = access_log_var != "none"

    print(f"🚀 Starting on {host}:{port} with {workers} workers")

    # Configure loop and http settings based on platform
    uvicorn_config = {
        "app": "app.api.app:create_app",
        "host": host,
        "port": port,
        "log_level": log_level,
        "factory": True,
        "access_log": use_access_log,
        "timeout_keep_alive": timeout_keepalive,
        "timeout_graceful_shutdown": timeout_graceful_shutdown,
        "proxy_headers": True,
        "forwarded_allow_ips": "*",
    }
    
    # Only set workers if not Windows (Windows doesn't support multiple workers well)
    if workers > 1 and sys.platform != "win32":
        uvicorn_config["workers"] = workers
    
    # Use uvloop and httptools only on non-Windows platforms
    if sys.platform != "win32":
        uvicorn_config["loop"] = "uvloop"
        uvicorn_config["http"] = "httptools"

    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()
