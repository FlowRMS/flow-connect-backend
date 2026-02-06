from commons.db.v6.base import BaseModel


class PyConnectPosBaseModel(BaseModel):
    __abstract__ = True
    __table_args__ = {"schema": "connect_pos", "extend_existing": True}
