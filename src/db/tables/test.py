import sqlalchemy as sa

from src.db.engine import sa_metadata

test_table = sa.Table(
    "test", sa_metadata, sa.Column("id", sa.Integer, nullable=False, primary_key=True)
)
