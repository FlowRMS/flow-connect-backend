if __name__ == "__main__":
    import sys
    import uvicorn
    import argparse
    from app.core.config.base_settings import get_settings_local
    from app.core.config.settings import Settings

    parser = argparse.ArgumentParser()
    _ = parser.add_argument(
        "--env",
        type=str,
        default="dev",
        help="The environment to run the app in (e.g., dev, staging, prod).",
    )
    args = parser.parse_args()

    settings = get_settings_local(env=args.env, cls=Settings)
    
    # Configure uvicorn options based on platform
    uvicorn_config = {
        "app": "app.api.app:create_app",
        "port": 8006,
        "factory": True,
        "reload": True,
    }
    
    # Use uvloop only on non-Windows platforms
    if sys.platform != "win32":
        uvicorn_config["loop"] = "uvloop"
    
    uvicorn.run(**uvicorn_config)
