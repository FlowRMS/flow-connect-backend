

from typing import Any

import strawberry


@strawberry.type
class EntityDataResponse:


    entity_type: str
    entity_id: str
    data: strawberry.scalars.JSON  

