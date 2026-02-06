from commons.db.v6.base import BaseModel


class PyConnectGeographyBaseModel(BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "connect_geography", "extend_existing": True}
