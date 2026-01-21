from typing import Any

from commons.db.v6.commission import Adjustment, CheckDetail, Credit, Invoice
from sqlalchemy import Connection, event, update


@event.listens_for(CheckDetail, "after_insert")
def lock_entities_after_check_detail_insert(
    mapper: Any, connection: Connection, target: CheckDetail
) -> None:
    if target.invoice_id:
        _ = connection.execute(
            update(Invoice).where(Invoice.id == target.invoice_id).values(locked=True)
        )
    if target.credit_id:
        _ = connection.execute(
            update(Credit).where(Credit.id == target.credit_id).values(locked=True)
        )
    if target.adjustment_id:
        _ = connection.execute(
            update(Adjustment)
            .where(Adjustment.id == target.adjustment_id)
            .values(locked=True)
        )


@event.listens_for(CheckDetail, "after_delete")
def unlock_entities_after_check_detail_delete(
    mapper: Any, connection: Connection, target: CheckDetail
) -> None:
    if target.invoice_id:
        _ = connection.execute(
            update(Invoice).where(Invoice.id == target.invoice_id).values(locked=False)
        )
    if target.credit_id:
        _ = connection.execute(
            update(Credit).where(Credit.id == target.credit_id).values(locked=False)
        )
    if target.adjustment_id:
        _ = connection.execute(
            update(Adjustment)
            .where(Adjustment.id == target.adjustment_id)
            .values(locked=False)
        )
