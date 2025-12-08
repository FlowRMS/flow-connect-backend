"""removing company id

Revision ID: c4b9f784a484
Revises: c3d4e5f60718
Create Date: 2025-12-08 12:56:52.727466

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from app.graphql.links.models.entity_type import EntityType


# revision identifiers, used by Alembic.
revision: str = 'c4b9f784a484'
down_revision: str | None = 'c3d4e5f60718'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.execute(f"""
        INSERT INTO pycrm.link_relations (id, source_entity_id, source_entity_type, target_entity_id, target_entity_type, created_at, created_by_id)
        SELECT 
            gen_random_uuid(), 
            id, 
            {EntityType.CONTACT.value}, 
            company_id, 
            {EntityType.COMPANY.value}, 
            created_at, 
            created_by_id
        FROM pycrm.contacts
        WHERE company_id IS NOT NULL;
    """)    
    op.drop_column('contacts', 'company_id', schema="pycrm")
    
def downgrade() -> None:
    op.add_column('contacts', sa.Column('company_id', sa.UUID(), nullable=True), schema="pycrm")