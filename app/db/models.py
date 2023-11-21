from typing import Optional

from tortoise import fields
from tortoise.exceptions import DoesNotExist

from app.base.base_models import BaseModel
from app.db.schemas import BaseUserCreate, BaseRouteCreate


class User(BaseModel):
    tg_id = fields.IntField()
    first_name = fields.CharField(max_length=128)

    @classmethod
    async def get_by_tg_id(cls, tg_id: int) -> Optional["User"]:
        try:
            query = cls.get_or_none(tg_id=tg_id)
            user = await query
            return user
        except DoesNotExist:
            return None
        
    @classmethod
    async def create(cls, user: BaseUserCreate) -> "User":
        user_dict = user.model_dump()
        model = cls(**user_dict)
        await model.save()
        return model
    
    class Meta:
        table = "users"


class FavoriteRoute(BaseModel):
    start_station = fields.CharField(max_length=128)
    finish_station = fields.CharField(max_length=128)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(
        "models.User", related_name="selected_routes", to_field="uuid", on_delete=fields.CASCADE
    )

    async def create(cls, route: BaseRouteCreate) -> "FavoriteRoute":
        route_dict = route.model_dump()
        model = cls(**route_dict)
        await model.save()
        return model
    
    class Meta:
        table = "FavoriteRotes"
