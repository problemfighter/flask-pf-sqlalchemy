from common.pff_common_exception import PFFCommonException
from pf_sqlalchemy.crud.pfs_crud_service import PfsCrudService
from pf_sqlalchemy.db.orm import Base
from pfms.pfapi.base.pfms_base_schema import PfBaseSchema
from pfms.pfapi.rr.pfms_request_respons import PfRequestResponse

pfs_crud = PfsCrudService()


class PfsRestHelperService(PfRequestResponse):
    model: Base = None

    def __init__(self, model: Base = None):
        self.model = model

    def rest_check_id(self, dto_schema: PfBaseSchema, message="Invalid Id"):
        if not dto_schema.id:
            raise PFFCommonException(message)

    def rest_get_id(self, dto_schema: PfBaseSchema, message="Invalid Id"):
        self.check_id(dto_schema, message)
        return dto_schema.id

    def _get_model(self, entity: Base = None, message="Invalid Model"):
        if not entity and self.model:
            entity = self.model
        else:
            raise PFFCommonException(message)
        return entity

    def rest_get_value_by_id(self, id: int, entity: Base = None):
        entity = self._get_model(entity)
        return entity.query.filter_by(id=id).first()

    def rest_create(self, request_dto: PfBaseSchema, response_dto: PfBaseSchema = None, message: str = "Successfully Created"):
        validated_model = self.json_request_process(request_dto)
        pfs_crud.save(validated_model)
        if not response_dto:
            return self.success(message)
        return self.json_data_response(validated_model, response_dto)

    def rest_hard_delete(self, id: int):
        pass

    def rest_delete(self, id: int):
        pass

    def rest_details(self, id: int):
        pass

    def rest_list(self, dto_schema: PfBaseSchema, pagination: bool = True, sort: bool = True):
        pass
