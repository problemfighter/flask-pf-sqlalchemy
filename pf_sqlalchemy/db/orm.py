from flask_sqlalchemy import SQLAlchemy
from util.common_util import get_uuid

database = SQLAlchemy()


class Base(database.Model):
    __abstract__ = True
    id = database.Column(database.BigInteger, primary_key=True)
    created = database.Column(database.DateTime, default=database.func.now())
    updated = database.Column(database.DateTime, default=database.func.now(), onupdate=database.func.now())
    uuid = database.Column(database.String(50), default=get_uuid())
    is_deleted = database.Column(database.Boolean, default=False)


# Dummy Model
class BaseModel(Base):
    pass
