from typing import Annotated
from uuid import UUID

from advanced_alchemy.extensions.litestar.dto import SQLAlchemyDTO
from advanced_alchemy.extensions.litestar.providers import create_service_dependencies
from advanced_alchemy.filters import (
    FilterTypes,
)
from advanced_alchemy.service import OffsetPagination

from litestar import get
from litestar.controller import Controller
from litestar.dto import DTOConfig
from litestar.params import Dependency

from ..services import UserService
from ..models import UserModel



class UserDTO(SQLAlchemyDTO[UserModel]):
    config = DTOConfig(
        exclude={
            "password",
            "created_at",
            "updated_at",
            "roles.0.created_at",
            "roles.0.updated_at",
        },
        max_nested_depth=1,
    )


class UserController(Controller):
    dependencies = create_service_dependencies(
        UserService,
        key="roles_service",
        load=[UserModel.roles],
        filters={
            "id_filter": UUID,
            "created_at": True,
            "updated_at": True,
            "pagination_type": "limit_offset",
        },
    )

    return_dto = UserDTO

    @get(operation_id="ListUsers", path="/users")
    async def list_users(
        self,
        roles_service: UserService,
        filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[UserModel]:
        results, total = await roles_service.list_and_count(*filters)
        return roles_service.to_schema(data=results, total=total, filters=filters)
