"""add_auth

Revision ID: e6f9b24a4ff7
Revises: d5afd58be157
Create Date: 2022-09-11 18:05:31.755248

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e6f9b24a4ff7"
down_revision = "d5afd58be157"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "comments",
        sa.Column(
            "user",
            sa.Integer(),
            nullable=False,
            comment="Пользователь оставивший коммент",
        ),
    )
    op.create_foreign_key(None, "comments", "users", ["user"], ["id"])
    op.add_column(
        "posts",
        sa.Column(
            "user",
            sa.Integer(),
            nullable=False,
            comment="Пользователь написавший пост",
        ),
    )
    op.alter_column(
        "posts",
        "created_dt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=False,
        existing_comment="Дата публикации",
    )
    op.create_unique_constraint(None, "posts", ["id"])
    op.create_foreign_key(None, "posts", "users", ["user"], ["id"])
    op.add_column(
        "users", sa.Column("password_hash", sa.Text(), nullable=False)
    )
    op.add_column("users", sa.Column("disabled", sa.BOOLEAN(), nullable=True))
    op.create_unique_constraint(None, "users", ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "disabled")
    op.drop_column("users", "password_hash")
    op.alter_column(
        "posts",
        "created_dt",
        existing_type=postgresql.TIMESTAMP(),
        nullable=True,
        existing_comment="Дата публикации",
    )
    op.drop_column("posts", "user")
    op.drop_column("comments", "user")
    # ### end Alembic commands ###
