from common.pff_common_exception import PFFCommonException
from pf_sqlalchemy.db.orm import database, Base
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
