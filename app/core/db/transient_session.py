from sqlalchemy.ext.asyncio import AsyncSession


class TransientSession(AsyncSession): ...


class TenantSession(AsyncSession):
    """Marker type for multi-tenant database sessions.

    Used to distinguish tenant-scoped sessions from the orgs database session
    in dependency injection. Repositories that need tenant data (connect_pos schema)
    should depend on TenantSession, not AsyncSession.
    """

    ...
