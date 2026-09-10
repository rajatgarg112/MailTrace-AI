"""initial_phase1_schema

Revision ID: 001_initial_phase1_schema
Revises:
Create Date: 2026-09-10 15:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_phase1_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. emails table
    op.create_table(
        'emails',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('message_id', sa.String(length=255), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('sender', sa.String(length=255), nullable=False),
        sa.Column('recipients', sa.Text(), nullable=False, comment='Comma-separated string of recipient email addresses'),
        sa.Column('subject', sa.String(length=500), nullable=True),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('RECEIVED', 'SCANNING', 'DECISION', 'DELIVERED', 'WARNING', 'QUARANTINED', 'REJECTED', 'FAILED', 'UNKNOWN', name='emailstatus', native_enum=False), nullable=False),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_emails_message_id'), 'emails', ['message_id'], unique=False)
    op.create_index(op.f('ix_emails_sender'), 'emails', ['sender'], unique=False)
    op.create_index(op.f('ix_emails_status'), 'emails', ['status'], unique=False)
    op.create_index(op.f('ix_emails_user_id'), 'emails', ['user_id'], unique=False)

    # 3. email_events table
    op.create_table(
        'email_events',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email_id', sa.String(length=36), nullable=False),
        sa.Column('from_status', sa.Enum('RECEIVED', 'SCANNING', 'DECISION', 'DELIVERED', 'WARNING', 'QUARANTINED', 'REJECTED', 'FAILED', 'UNKNOWN', name='emailstatus', native_enum=False), nullable=True),
        sa.Column('to_status', sa.Enum('RECEIVED', 'SCANNING', 'DECISION', 'DELIVERED', 'WARNING', 'QUARANTINED', 'REJECTED', 'FAILED', 'UNKNOWN', name='emailstatus', native_enum=False), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('details', sa.Text(), nullable=True, comment='Optional human-readable or JSON details describing the event context'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_email_events_email_id'), 'email_events', ['email_id'], unique=False)
    op.create_index(op.f('ix_email_events_event_type'), 'email_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_email_events_from_status'), 'email_events', ['from_status'], unique=False)
    op.create_index(op.f('ix_email_events_timestamp'), 'email_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_email_events_to_status'), 'email_events', ['to_status'], unique=False)

    # 4. analysis_results table
    op.create_table(
        'analysis_results',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email_id', sa.String(length=36), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False, comment='Numeric risk score (e.g. 0.0 to 1.0 or 0 to 100)'),
        sa.Column('verdict', sa.Enum('SAFE', 'SUSPICIOUS', 'MALICIOUS', 'UNKNOWN', name='verdict', native_enum=False), nullable=False),
        sa.Column('detection_reasons', sa.Text(), nullable=True, comment='JSON list or text summary of detection signals and evidence rationale'),
        sa.Column('analysis_duration_ms', sa.Float(), nullable=True, comment='Analysis pipeline execution duration in milliseconds'),
        sa.Column('details_json', sa.Text(), nullable=True, comment='Flexible JSON storage for full module outputs (AI, headers, URLs, attachments, etc.)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['email_id'], ['emails.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email_id'),
    )
    op.create_index(op.f('ix_analysis_results_email_id'), 'analysis_results', ['email_id'], unique=True)
    op.create_index(op.f('ix_analysis_results_risk_score'), 'analysis_results', ['risk_score'], unique=False)
    op.create_index(op.f('ix_analysis_results_verdict'), 'analysis_results', ['verdict'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_analysis_results_verdict'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_risk_score'), table_name='analysis_results')
    op.drop_index(op.f('ix_analysis_results_email_id'), table_name='analysis_results')
    op.drop_table('analysis_results')

    op.drop_index(op.f('ix_email_events_to_status'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_timestamp'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_from_status'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_event_type'), table_name='email_events')
    op.drop_index(op.f('ix_email_events_email_id'), table_name='email_events')
    op.drop_table('email_events')

    op.drop_index(op.f('ix_emails_user_id'), table_name='emails')
    op.drop_index(op.f('ix_emails_status'), table_name='emails')
    op.drop_index(op.f('ix_emails_sender'), table_name='emails')
    op.drop_index(op.f('ix_emails_message_id'), table_name='emails')
    op.drop_table('emails')

    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
