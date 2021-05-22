from common.pff_common_exception import PFFCommonException
from flask import request
from pf_sqlalchemy.crud.pfs_crud_service import PfsCrudService
from pf_sqlalchemy.db.orm import Base
from pfms.pfapi.base.pfms_base_schema import PfBaseSchema
from pfms.pfapi.rr.pfms_request_respons import PfRequestResponse
from sqlalchemy import and_, or_

pfs_crud = PfsCrudService()


class PfsRestHelperService(PfRequestResponse):
    model = None

    def __init__(self, model):
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

    def rest_get_value_by_id(self, model_id: int, is_deleted: bool = False, entity: Base = None, query_condition=None):
        entity = self._get_model(entity)
        query = query_condition
        if not query_condition:
            query = entity.query
        return query.filter(and_(entity.id == model_id, entity.isDeleted == is_deleted)).first()

    def rest_validate_and_save(self, request_dto: PfBaseSchema):
        validated_model = self.json_request_process(request_dto)
        pfs_crud.save(validated_model)
        return validated_model

    def rest_validate_and_update_by_id(self, model_id, request_dto: PfBaseSchema):
        model = self.rest_get_value_by_id(model_id)
        validated_model = self.json_request_process(request_dto, model)
        pfs_crud.save(validated_model)
        return validated_model

    def rest_validate_and_update(self, request_dto: PfBaseSchema):
        model_id = self.rest_get_requested_model_id()
        return self.rest_validate_and_update_by_id(model_id, request_dto)

    def rest_create(self, request_dto: PfBaseSchema, response_dto: PfBaseSchema = None, message: str = "Successfully Created"):
        validated_model = self.rest_validate_and_save(request_dto)
        if not response_dto:
            return self.success(message)
        return self.json_data_response(validated_model, response_dto)

    def rest_update(self, request_dto: PfBaseSchema, response_dto: PfBaseSchema = None, message: str = "Successfully Updated"):
        validated_model = self.rest_validate_and_update(request_dto)
        if not response_dto:
            return self.success(message)
        return self.json_data_response(validated_model, response_dto)

    def rest_by_id_or_exception(self, model_id: int, message: str = "Requested data not exist!", is_deleted: bool = False, query_condition=None):
        model = self.rest_get_value_by_id(model_id, is_deleted, query_condition=query_condition)
        if not model:
            raise PFFCommonException(message)
        return model

    def rest_hard_delete(self, model_id: int):
        pass

    def rest_delete(self, model_id: int, success: str = "Successfully Deleted", error: str = "Requested data not exist!"):
        model = self.rest_by_id_or_exception(model_id, error)
        model.isDeleted = True
        pfs_crud.save(model)
        return self.success(success)

    def rest_restore(self, model_id: int, success: str = "Successfully Restored", error: str = "Requested data not exist!"):
        model = self.rest_by_id_or_exception(model_id, error, True)
        model.isDeleted = False
        pfs_crud.save(model)
        return self.success(success)

    def rest_details(self, model_id: int, response_dto: PfBaseSchema, message: str = "Requested data not exist!", query_condition=None):
        model = self.rest_by_id_or_exception(model_id, message, query_condition=query_condition)
        return self.json_data_response(model, response_dto)

    def rest_order_by(self, model, default_field="id", default_order="desc"):
        sort_field = self.request().get_requested_value("sort-field")
        if not sort_field:
            sort_field = default_field

        sort_order = self.request().get_requested_value("sort-order")
        if not sort_order:
            sort_order = default_order
        elif sort_order and (sort_order != "asc" and sort_order != "desc"):
            sort_order = default_order

        if sort_order == "asc":
            return model.order_by(getattr(self.model, sort_field).asc())
        return model.order_by(getattr(self.model, sort_field).desc())

    def pagination_params(self, item_per_page=25):
        page: int = self.request().get_query_param_value('page', type=int)
        if not page:
            page = 0
        per_page: int = self.request().get_query_param_value('per-page', type=int)
        if not per_page:
            per_page = item_per_page
        return {"page": page, "per_page": per_page}

    def rest_pagination(self, model, item_per_page=25):
        pagination = self.pagination_params(item_per_page)
        return model.paginate(page=pagination['page'], per_page=pagination['per_page'], error_out=False)

    def _rest_search(self, search_fields: list, query, search_text: str = None):
        like = []
        search = self.request().get_search_string()
        if search_text:
            search = search_text
        if search:
            for field in search_fields:
                like.append(getattr(self.model, field).ilike("%{}%".format(search)))
            if like:
                return query.filter(or_(*like))
        return query

    def rest_list(self, dto_schema: PfBaseSchema, search: list = None, default_sort: str = 'id', pagination: bool = True, sort: bool = True, model=None, is_deleted=False, default_order: str = "desc", search_text: str = None, per_page=25):
        query = model
        if not model:
            query = self.model.query
        query = query.filter(getattr(self.model, "isDeleted") == is_deleted)

        if sort:
            query = self.rest_order_by(query, default_sort, default_order)

        if search and self.model:
            query = self._rest_search(search, query, search_text=search_text)

        if pagination:
            result = self.rest_pagination(query, item_per_page=per_page)
            return self.json_pagination_response(result, dto_schema)
        else:
            result = query.all()
            return self.json_list_response(result, dto_schema)

