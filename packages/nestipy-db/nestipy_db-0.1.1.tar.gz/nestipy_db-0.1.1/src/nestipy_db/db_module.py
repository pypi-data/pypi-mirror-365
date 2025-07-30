from typing import Annotated

from nestipy.common import Module
from nestipy.dynamic_module import NestipyModule
from nestipy.ioc import Inject
from nestipy.metadata import Reflect

from .db_builder import ConfigurableModuleClass, DB_CONFIG, DbConfig
from .db_command import DbCommand
from .db_meta import DbMetadata
from .db_model import BaseModel as Model
from .db_service import DbService


@Module(
    providers=[
        DbService,
        DbCommand,
    ]
)
class DbModule(ConfigurableModuleClass, NestipyModule):
    _models: list[Model] = []
    _config: Annotated[DbConfig, Inject(DB_CONFIG)]
    _service: Annotated[DbService, Inject()]

    async def on_startup(self):
        models = Reflect.get_metadata(self.__class__, DbMetadata.Models, [])
        self._setup_model((self._config.models or []) + models)
        db, _ = self._service.get_connection()
        await db.connect()

    async def on_shutdown(self):
        db, _ = self._service.get_connection()
        await db.disconnect()

    @classmethod
    def for_feature(cls, *models: Model):
        for m in models:
            if (
                Reflect.get_metadata(m, DbMetadata.ModelMeta, False)
                and m not in cls._models
            ):
                cls._models.append(m)
                Reflect.set_metadata(cls, DbMetadata.Models, cls._models)
        return cls

    def _setup_model(self, models: list[Model]):
        db, registry = self._service.get_connection()
        for model in models:
            model.add_to_registry(registry, on_conflict="replace", database=db)
