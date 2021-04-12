from common.pff_common_exception import PFFCommonException
from pf_sqlalchemy.db.orm import database, Base
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from pf_sqlalchemy.crud.pfs_crud_exception import parse_integrity_error


class PfsCrudService:

    def _handle_exception(self, exception: Exception):
        if isinstance(exception, IntegrityError):
            raise PFFCommonException(parse_integrity_error(exception))
        raise PFFCommonException(str(exception))

    def save(self, model: Base):
        try:
            database.session.add(model)
            database.session.commit()
        except Exception as e:
            self._handle_exception(e)

    def save_all(self, models: list):
        try:
            database.session.add_all(models)
            database.session.commit()
        except Exception as e:
            self._handle_exception(e)

    def delete(self, model: Base):
        try:
            database.session.delete(model)
            database.session.commit()
        except Exception as e:
            self._handle_exception(e)

    def raw_query(self, sql):
        try:
            connection = database.engine.connect()
            return connection.execute(text(sql))
        except Exception as e:
            self._handle_exception(e)


