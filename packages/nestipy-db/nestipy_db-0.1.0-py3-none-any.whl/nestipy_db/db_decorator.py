from typing import Type, cast, Callable
from edgy import Model as edgy_Model
from nestipy.metadata import SetMetadata

from .db_meta import DbMetadata
from .db_model import BaseModel


def Model() -> Callable[[Type], BaseModel | Type[edgy_Model]]:
    decorator = SetMetadata(DbMetadata.ModelMeta, True)

    def class_decorator(cls: Type) -> BaseModel:
        cls = decorator(cls)
        return cast(BaseModel, cls)

    return class_decorator
