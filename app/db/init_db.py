from tortoise import Tortoise

from app.settings.config import settings

def get_app_list():
    app_list = [f"{settings.APPLICATIONS_MODULE}.{app}.models" for app in settings.APPLICATIONS]
    return app_list

async def init(db_url: str | None = None):
    await Tortoise.init(
        db_url=db_url | settings.DB_URL,
        modules=get_app_list()
    )

    await Tortoise.generate_schemas()