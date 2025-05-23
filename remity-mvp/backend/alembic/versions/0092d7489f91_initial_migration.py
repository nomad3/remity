"""Initial migration

Revision ID: 0092d7489f91
Revises: 
Create Date: 2025-04-08 01:32:28.074256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0092d7489f91'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=True),
    sa.Column('phone_number', sa.String(length=50), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('kyc_status', sa.Enum('PENDING', 'VERIFIED', 'REJECTED', 'REQUIRES_REVIEW', name='kyc_status_enum'), nullable=False),
    sa.Column('kyc_provider_reference', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), server_default=sa.text('false'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_kyc_status'), ['kyc_status'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_phone_number'), ['phone_number'], unique=False)

    op.create_table('audit_logs',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('action', sa.String(length=255), nullable=False),
    sa.Column('ip_address', postgresql.INET(), nullable=True),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_audit_logs_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_logs'))
    )
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_audit_logs_action'), ['action'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_logs_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_audit_logs_user_id'), ['user_id'], unique=False)

    op.create_table('recipients',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('full_name', sa.String(length=255), nullable=False),
    sa.Column('country_code', sa.String(length=2), nullable=False),
    sa.Column('payout_method', sa.String(length=50), nullable=False),
    sa.Column('payout_details', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_recipients_user_id_users'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_recipients'))
    )
    with op.batch_alter_table('recipients', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_recipients_country_code'), ['country_code'], unique=False)
        batch_op.create_index(batch_op.f('ix_recipients_user_id'), ['user_id'], unique=False)

    op.create_table('transactions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('recipient_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('QUOTE_CREATED', 'PENDING_PAYMENT', 'PAYMENT_RECEIVED', 'PENDING_APPROVAL', 'PROCESSING', 'PAYOUT_INITIATED', 'PAYOUT_COMPLETED', 'DELIVERED', 'FAILED', 'CANCELLED', 'MANUALLY_REJECTED', 'REFUNDED', name='transaction_status_enum'), nullable=False),
    sa.Column('source_currency', sa.String(length=3), nullable=False),
    sa.Column('target_currency', sa.String(length=3), nullable=False),
    sa.Column('source_amount', sa.Numeric(precision=19, scale=8), nullable=False),
    sa.Column('target_amount', sa.Numeric(precision=19, scale=8), nullable=False),
    sa.Column('exchange_rate', sa.Numeric(precision=19, scale=8), nullable=False),
    sa.Column('remity_fee', sa.Numeric(precision=19, scale=8), nullable=False),
    sa.Column('payment_provider_fee', sa.Numeric(precision=19, scale=8), nullable=False),
    sa.Column('estimated_delivery_time', sa.String(length=100), nullable=True),
    sa.Column('onramp_payment_intent_id', sa.String(length=255), nullable=True),
    sa.Column('onramp_payment_status', sa.String(length=50), nullable=True),
    sa.Column('offramp_payout_reference', sa.String(length=255), nullable=True),
    sa.Column('offramp_payout_status', sa.String(length=50), nullable=True),
    sa.Column('failure_reason', sa.Text(), nullable=True),
    sa.Column('reviewed_by_user_id', sa.UUID(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['recipient_id'], ['recipients.id'], name=op.f('fk_transactions_recipient_id_recipients')),
    sa.ForeignKeyConstraint(['reviewed_by_user_id'], ['users.id'], name=op.f('fk_transactions_reviewed_by_user_id_users')),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_transactions_user_id_users')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_transactions'))
    )
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_transactions_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_offramp_payout_reference'), ['offramp_payout_reference'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_onramp_payment_intent_id'), ['onramp_payment_intent_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_recipient_id'), ['recipient_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_reviewed_by_user_id'), ['reviewed_by_user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_source_currency'), ['source_currency'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_target_currency'), ['target_currency'], unique=False)
        batch_op.create_index(batch_op.f('ix_transactions_user_id'), ['user_id'], unique=False)

    op.create_table('internal_ledger',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('transaction_id', sa.UUID(), nullable=True),
    sa.Column('event_type', sa.String(length=100), nullable=False),
    sa.Column('currency', sa.String(length=10), nullable=False),
    sa.Column('amount', sa.Numeric(precision=19, scale=8), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], name=op.f('fk_internal_ledger_transaction_id_transactions')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_internal_ledger'))
    )
    with op.batch_alter_table('internal_ledger', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_internal_ledger_event_type'), ['event_type'], unique=False)
        batch_op.create_index(batch_op.f('ix_internal_ledger_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_internal_ledger_transaction_id'), ['transaction_id'], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('internal_ledger', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_internal_ledger_transaction_id'))
        batch_op.drop_index(batch_op.f('ix_internal_ledger_timestamp'))
        batch_op.drop_index(batch_op.f('ix_internal_ledger_event_type'))

    op.drop_table('internal_ledger')
    with op.batch_alter_table('transactions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_transactions_user_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_target_currency'))
        batch_op.drop_index(batch_op.f('ix_transactions_status'))
        batch_op.drop_index(batch_op.f('ix_transactions_source_currency'))
        batch_op.drop_index(batch_op.f('ix_transactions_reviewed_by_user_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_recipient_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_onramp_payment_intent_id'))
        batch_op.drop_index(batch_op.f('ix_transactions_offramp_payout_reference'))
        batch_op.drop_index(batch_op.f('ix_transactions_created_at'))

    op.drop_table('transactions')
    with op.batch_alter_table('recipients', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_recipients_user_id'))
        batch_op.drop_index(batch_op.f('ix_recipients_country_code'))

    op.drop_table('recipients')
    with op.batch_alter_table('audit_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_audit_logs_user_id'))
        batch_op.drop_index(batch_op.f('ix_audit_logs_timestamp'))
        batch_op.drop_index(batch_op.f('ix_audit_logs_action'))

    op.drop_table('audit_logs')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_phone_number'))
        batch_op.drop_index(batch_op.f('ix_users_kyc_status'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    # ### end Alembic commands ###
