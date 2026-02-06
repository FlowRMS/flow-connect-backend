import os
from collections.abc import Iterable
from typing import Any

import aioinject

from app.core.flow_connect_api.flow_connect_api_client import FlowConnectApiClient

api_client_providers: Iterable[aioinject.Provider[Any]] = []

if os.environ.get("FLOW_CONNECT_API_URL"):
    api_client_providers = [
        aioinject.Scoped(FlowConnectApiClient),
    ]
