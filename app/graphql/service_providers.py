import app.graphql
from app.graphql.provider_discovery import discover_providers

service_providers = discover_providers(
    modules=app.graphql,
    class_suffix="service",
)
