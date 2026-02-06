import os
from pathlib import Path

import dotenv

import app.graphql.connections
import app.graphql.geography
import app.graphql.organizations
import app.graphql.pos
import app.graphql.settings
from app.graphql.di.discovery import discover_providers

# Load environment files before checking ORGS_DB_URL
# pydantic-settings reads these files but doesn't set os.environ
# Use absolute paths to handle different working directories
_project_root = Path(__file__).parent.parent.parent.parent
for env_file in [".env", ".env.local", ".env.dev"]:
    dotenv.load_dotenv(_project_root / env_file, override=False)

# Only register organization providers if ORGS_DB_URL is configured
repository_providers = []
if os.environ.get("ORGS_DB_URL"):
    repository_providers = list(
        discover_providers(
            modules=[
                app.graphql.organizations,
                app.graphql.connections,
                app.graphql.geography,
                app.graphql.pos,
                app.graphql.settings,
            ],
            class_suffix="repository",
        )
    )
