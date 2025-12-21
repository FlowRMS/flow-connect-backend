"""merge_pdf_templates_and_contacts

Revision ID: 72f372e4ca67
Revises: add_pdf_templates, add_contact_type_contacts
Create Date: 2025-12-21 08:55:35.958097

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '72f372e4ca67'
down_revision: str | None = ('add_pdf_templates', 'add_contact_type_contacts')
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    pass
    
def downgrade() -> None:
    pass
