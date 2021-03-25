from common.pff_common_exception import PFFCommonException
from pf_sqlalchemy.crud.pfs_crud_service import PfsCrudService
from pf_sqlalchemy.db.orm import Base
from pfms.pfapi.base.pfms_base_schema import PfBaseSchema
from pfms.pfapi.rr.pfms_request_respons import PfRequestResponse
from sqlalchemy import and_, or_

pfs_crud = PfsCrudService()


class PfsRestHelperService(PfRequestResponse):
    model = None

    def __init__(self, model=None):
        self.model = model

    def rest_get_requested_model_id(self, message="Invalid Id"):
        model_id = self.request().get_requested_data_value("id")
        if not model_id:
            raise PFFCommonException(message)
        return model_id

    def rest_get_id(self, dto_schema: PfBaseSchema, message="Invalid Id"):
        self.check_id(dto_schema, message)
        return dto_schema.id

    def _get_model(self, entity: Base = None, message="Invalid Model"):
        if not entity and self.model:
            entity = self.model
        else:
            raise PFFCommonException(message)
        return entity

    def rest_get_value_by_id(self, model_id: int, is_deleted: bool = False, entity: Base = None):
        entity = self._get_model(entity)
        return entity.query.filter(and_(entity.id == model_id, entity.is_deleted == is_deleted)).first()

    def rest_create(self, request_dto: PfBaseSchema, response_dto: PfBaseSchema = None, message: str = "Successfully Created"):
        validated_model = self.json_request_process(request_dto)
        pfs_crud.save(validated_model)
        if not response_dto:
            return self.success(message)
        return self.json_data_response(validated_model, response_dto)

    def rest_update(self, request_dto: PfBaseSchema, response_dto: PfBaseSchema = None, message: str = "Successfully Updated"):
        model_id = self.rest_get_requested_model_id()
        model = self.rest_get_value_by_id(model_id)
        validated_model = self.json_request_process(request_dto, model)
        pfs_crud.save(validated_model)
        if not response_dto:
            return self.success(message)
        return self.json_data_response(validated_model, response_dto)

    def rest_by_id_or_exception(self, model_id: int, message: str = "Requested data not exist!", is_deleted: bool = False):
        model = self.rest_get_value_by_id(model_id, is_deleted)
        if not model:
            raise PFFCommonException(message)
        return model

    def rest_hard_delete(self, model_id: int):
        pass

    def rest_delete(self, model_id: int, success: str = "Successfully Deleted", error: str = "Requested data not exist!"):
        model = self.rest_by_id_or_exception(model_id, error)
        model.is_deleted = True
        pfs_crud.save(model)
        return self.success(success)

    def rest_restore(self, model_id: int, success: str = "Successfully Restored", error: str = "Requested data not exist!"):
        model = self.rest_by_id_or_exception(model_id, error, True)
        model.is_deleted = False
        pfs_crud.save(model)
        return self.success(success)

    def rest_details(self, model_id: int, response_dto: PfBaseSchema, message: str = "Requested data not exist!"):
        model = self.rest_by_id_or_exception(model_id, message)
        return self.json_data_response(model, response_dto)

    def _rest_search(self, search_fields: list, query):
        like = []
        search = self.request().get_search_string()
        if search:
            for field in search_fields:
                like.append(getattr(self.model, field).ilike("%{}%".format(search)))
            if like:
                return query.filter(or_(*like))
        return query

    def rest_list(self, dto_schema: PfBaseSchema, search: list = None, default_sort: str = 'id', pagination: bool = True, sort: bool = True, model=None):
        query = model
        if not model:
            query = self.model.query

        if sort:
            query = self.request().add_order_by(query, default_sort)

        if search and self.model:
            query = self._rest_search(search, query)

        if pagination:
            result = self.request().add_pagination(query)
        else:
            result = query.all()

        return self.json_pagination_response(result, dto_schema)
