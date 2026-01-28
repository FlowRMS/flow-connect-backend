import app.graphql
import app.integrations
import app.workers
from app.graphql.provider_discovery import discover_providers

service_providers = discover_providers(
    modules=[app.graphql, app.integrations, app.workers],
    class_suffix="service",
)
