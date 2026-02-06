from __future__ import annotations

import uuid

from commons.db.v6.base import HasCreatedAt
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.graphql.geography.models.base import PyConnectGeographyBaseModel


class Country(PyConnectGeographyBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "countries"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(3), nullable=False, unique=True)

    subdivisions: Mapped[list[Subdivision]] = relationship(
        "Subdivision",
        back_populates="country",
        init=False,
    )


class Subdivision(PyConnectGeographyBaseModel, HasCreatedAt, kw_only=True):
    __tablename__ = "subdivisions"

    country_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("connect_geography.countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    iso_code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)

    country: Mapped[Country] = relationship(
        "Country",
        back_populates="subdivisions",
        init=False,
    )
