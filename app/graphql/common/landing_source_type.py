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
    FOLDERS = "folders"
    INVOICES = "invoices"
    CREDITS = "credits"
    ADJUSTMENTS = "adjustments"
    CHECKS = "checks"
    ORDER_ACKNOWLEDGEMENTS = "order_acknowledgements"
    PENDING_DOCUMENTS = "pending_documents"
    STATEMENTS = "statements"
