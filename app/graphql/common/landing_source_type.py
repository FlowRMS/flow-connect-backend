"""Landing page source type enum for generic landing page queries."""

from enum import Enum

import strawberry


@strawberry.enum
class LandingSourceType(Enum):
    """Enum representing different entity types for landing pages."""

    JOBS = "jobs"
    COMPANIES = "companies"
    CONTACTS = "contacts"
    TASKS = "tasks"
