import app.graphql
import app.integrations
from app.graphql.provider_discovery import discover_providers

repository_providers = discover_providers(
    modules=[app.graphql, app.integrations],
    class_suffix="repository",
)
