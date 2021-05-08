from flask_sqlalchemy import SQLAlchemy
from util.common_util import get_uuid

database = SQLAlchemy()


class PrimeBase(database.Model):
    __abstract__ = True


class Base(PrimeBase):
    __abstract__ = True
    id = database.Column("id", database.BigInteger, primary_key=True)
    created = database.Column("created", database.DateTime, default=database.func.now())
    updated = database.Column("updated", database.DateTime, default=database.func.now(), onupdate=database.func.now())
    uuid = database.Column("uuid", database.String(50), default=get_uuid())
    isDeleted = database.Column("is_deleted", database.Boolean, default=False)
    isActive = database.Column("is_active", database.Boolean, default=True)


# Dummy Model
class BaseModel(Base):
    pass
