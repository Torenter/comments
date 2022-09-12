"""first

Revision ID: d5afd58be157
Revises: 
Create Date: 2022-09-10 11:01:49.419493

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "d5afd58be157"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree;")
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False, comment="Текст поста"),
        sa.Column("likes", sa.Integer(), nullable=True, comment="Лаки"),
        sa.Column(
            "created_dt",
            sa.DateTime(),
            nullable=True,
            comment="Дата публикации",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False, comment="имя пользака"),
        sa.Column(
            "login",
            sa.String(),
            nullable=False,
            comment="Уникальный логин пользака",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("login"),
    )
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "post_id",
            sa.Integer(),
            nullable=False,
            comment="Пост к которому оставили коммент",
        ),
        sa.Column(
            "text", sa.Text(), nullable=False, comment="Текст комментария"
        ),
        sa.Column("likes", sa.Integer(), nullable=True, comment="Лаки"),
        sa.Column(
            "created_dt",
            sa.DateTime(),
            nullable=False,
            comment="Дата публикации",
        ),
        sa.Column(
            "path", sqlalchemy_utils.types.ltree.LtreeType(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["posts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_nodes_path",
        "comments",
        ["path"],
        unique=False,
        postgresql_using="gist",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "ix_nodes_path", table_name="comments", postgresql_using="gist"
    )
    op.drop_table("comments")
    op.drop_table("users")
    op.drop_table("posts")
    # ### end Alembic commands ###