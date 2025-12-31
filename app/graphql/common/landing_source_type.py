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
    NOTES = "notes"
    PRE_OPPORTUNITIES = "pre_opportunities"
    CAMPAIGNS = "campaigns"
    CUSTOMERS = "customers"
    FACTORIES = "factories"
    PRODUCTS = "products"
    QUOTES = "quotes"
    ORDERS = "orders"
    FILES = "files"
    INVOICES = "invoices"
    CREDITS = "credits"
    ADJUSTMENTS = "adjustments"
    CHECKS = "checks"
