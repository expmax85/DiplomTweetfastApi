"""init

Revision ID: f180c7a775e0
Revises:
Create Date: 2023-02-06 09:37:01.268007

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f180c7a775e0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=15), nullable=False),
        sa.Column("hashed_password", sa.String(length=100), nullable=True),
        sa.Column("inactive", sa.Boolean, default=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "followers",
        sa.Column(
            "follower_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True
        ),
        sa.Column(
            "followed_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True
        ),
    )
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("api_key", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tweets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tweet_media_ids", sa.ARRAY(sa.Integer()), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "likes",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tweet_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["tweet_id"],
            ["tweets.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("user_id", "tweet_id"),
    )
    op.create_table(
        "tweet_media",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("image", sa.String(), nullable=True),
        sa.Column("tweet_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["tweet_id"], ["tweets.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("tweet_media")
    op.drop_table("likes")
    op.drop_table("tweets")
    op.drop_table("tokens")
    op.drop_table("followers")
    op.drop_table("users")
    # ### end Alembic commands ###
