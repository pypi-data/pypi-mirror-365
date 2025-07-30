from dataclasses import dataclass, field

from nestipy.dynamic_module import ConfigurableModuleBuilder

from .db_model import BaseModel


@dataclass
class DbConfig:
    url: str = ""
    models: list[BaseModel] = field(default_factory=lambda: [])
    # options: dict = field(default_factory=lambda: {})


ConfigurableModuleClass, DB_CONFIG = (
    ConfigurableModuleBuilder[DbConfig]().set_method("for_root").build()
)
