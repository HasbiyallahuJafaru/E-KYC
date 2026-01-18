"""Add CAC entity type fields

Revision ID: 001_cac_entity_type
Revises: 
Create Date: 2026-01-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from app.core.types import JSONB


# revision identifiers, used by Alembic.
revision = '001_cac_entity_type'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add new fields to verification_results table to support different CAC entity types:
    - Limited Companies (Ltd/PLC): directors, shareholders, share capital
    - Business Names (BN): proprietors, nature of business
    - NGOs/Incorporated Trustees (IT): trustees, aims/objectives
    """
    # Add entity type field
    op.add_column('verification_results', 
        sa.Column('cac_entity_type', sa.String(50), nullable=True, 
                  comment='Entity type: LIMITED, PLC, BUSINESS_NAME, NGO, INCORPORATED_TRUSTEES')
    )
    
    # Add registered address field
    op.add_column('verification_results', 
        sa.Column('cac_registered_address', sa.String(500), nullable=True,
                  comment='Registered office address from CAC')
    )
    
    # Add entity-specific data storage (JSONB field for directors, shareholders, proprietors, trustees)
    op.add_column('verification_results', 
        sa.Column('cac_entity_data', JSONB, nullable=True,
                  comment='Entity-specific data (directors/shareholders for Ltd, proprietors for BN, trustees for NGO)')
    )


def downgrade() -> None:
    """Remove CAC entity type fields."""
    op.drop_column('verification_results', 'cac_entity_data')
    op.drop_column('verification_results', 'cac_registered_address')
    op.drop_column('verification_results', 'cac_entity_type')
