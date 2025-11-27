if __name__ == "__main__":
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
    uvicorn.run("app.api.app:create_app", port=8006, factory=True, reload=True, loop="uvloop")
