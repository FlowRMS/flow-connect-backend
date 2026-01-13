import app.core
import app.graphql
from app.graphql.provider_discovery import discover_providers

processor_providers = discover_providers(
    modules=[app.graphql, app.core],
    class_suffix="processor",
)
