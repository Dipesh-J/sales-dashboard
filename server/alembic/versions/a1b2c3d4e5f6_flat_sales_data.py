"""replace normalized schema with flat sales_data

Revision ID: a1b2c3d4e5f6
Revises: 99f535cccdb3
Create Date: 2026-03-10 13:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '99f535cccdb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop old normalized tables and create flat sales_data table."""
    # Drop old tables in dependency order
    op.drop_table('sales')
    op.drop_table('stores')
    op.drop_table('products')
    op.drop_table('regions')

    # Create new flat table
    op.create_table('sales_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('master_distributor', sa.String(), nullable=True),
        sa.Column('distributor', sa.String(), nullable=True),
        sa.Column('line_of_business', sa.String(), nullable=True),
        sa.Column('supplier', sa.String(), nullable=True),
        sa.Column('agency', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('segment', sa.String(), nullable=True),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('sub_brand', sa.String(), nullable=True),
        sa.Column('country', sa.String(), nullable=True),
        sa.Column('city', sa.String(), nullable=True),
        sa.Column('area', sa.String(), nullable=True),
        sa.Column('retailer_group', sa.String(), nullable=True),
        sa.Column('retailer_sub_group', sa.String(), nullable=True),
        sa.Column('channel', sa.String(), nullable=True),
        sa.Column('sub_channel', sa.String(), nullable=True),
        sa.Column('salesmen', sa.String(), nullable=True),
        sa.Column('order_number', sa.String(), nullable=True),
        sa.Column('customer', sa.String(), nullable=True),
        sa.Column('customer_account_name', sa.String(), nullable=True),
        sa.Column('customer_account_number', sa.String(), nullable=True),
        sa.Column('item', sa.String(), nullable=True),
        sa.Column('item_description', sa.String(), nullable=True),
        sa.Column('promo_item', sa.String(), nullable=True),
        sa.Column('foc_nonfoc', sa.String(), nullable=True),
        sa.Column('unit_selling_price', sa.Float(), nullable=True),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('invoice_date', sa.Date(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('month', sa.String(), nullable=True),
        sa.Column('invoiced_quantity', sa.Float(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Indexes for commonly filtered/queried columns
    op.create_index(op.f('ix_sales_data_id'), 'sales_data', ['id'], unique=False)
    op.create_index(op.f('ix_sales_data_master_distributor'), 'sales_data', ['master_distributor'], unique=False)
    op.create_index(op.f('ix_sales_data_distributor'), 'sales_data', ['distributor'], unique=False)
    op.create_index(op.f('ix_sales_data_line_of_business'), 'sales_data', ['line_of_business'], unique=False)
    op.create_index(op.f('ix_sales_data_category'), 'sales_data', ['category'], unique=False)
    op.create_index(op.f('ix_sales_data_brand'), 'sales_data', ['brand'], unique=False)
    op.create_index(op.f('ix_sales_data_country'), 'sales_data', ['country'], unique=False)
    op.create_index(op.f('ix_sales_data_city'), 'sales_data', ['city'], unique=False)
    op.create_index(op.f('ix_sales_data_channel'), 'sales_data', ['channel'], unique=False)
    op.create_index(op.f('ix_sales_data_invoice_date'), 'sales_data', ['invoice_date'], unique=False)
    op.create_index(op.f('ix_sales_data_year'), 'sales_data', ['year'], unique=False)


def downgrade() -> None:
    """Drop sales_data and recreate old normalized tables."""
    op.drop_table('sales_data')

    # Recreate old tables
    op.create_table('regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regions_id'), 'regions', ['id'], unique=False)
    op.create_index(op.f('ix_regions_name'), 'regions', ['name'], unique=True)

    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_name'), 'products', ['name'], unique=False)
    op.create_index(op.f('ix_products_brand'), 'products', ['brand'], unique=False)
    op.create_index(op.f('ix_products_category'), 'products', ['category'], unique=False)

    op.create_table('stores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('region_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stores_id'), 'stores', ['id'], unique=False)

    op.create_table('sales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('store_id', sa.Integer(), nullable=True),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_id'), 'sales', ['id'], unique=False)
    op.create_index(op.f('ix_sales_date'), 'sales', ['date'], unique=False)
