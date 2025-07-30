<p align="center">
  <a target="_blank">
    <img src="https://raw.githubusercontent.com/nestipy/nestipy/release-v1/nestipy.png" width="200" alt="Nestipy Logo" />
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/nestipy-db">
    <img src="https://img.shields.io/pypi/v/nestipy_db?color=%2334D058&label=pypi%20package" alt="Version">
  </a>
  <a href="https://pypi.org/project/nestipy-db">
    <img src="https://img.shields.io/pypi/pyversions/nestipy_db.svg?color=%2334D058" alt="Python">
  </a>
  <a href="https://github.com/tsiresymila1/nestipy/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/tsiresymila1/nestipy" alt="License">
  </a>
</p>

## NestipyDB

NestipyDB is the official database module for Nestipy. It is built on top of <a href="https://edgy.dymmond.com/" target="_blank">Edgy</a> and designed to be modular and configurable.

## Installation

NestipyDB depends on Edgy. Make sure to follow the <a href="https://edgy.dymmond.com/edgy#installation" target="_blank">Edgy installation guide</a> to set up dependencies for your specific database.

```bash
pip install nestipy-db
```

## Usage

First, in your `app_module.py`, replace the `url` in `DbConfig` with your own:

```python
from nestipy.common import Module
from nestipy_db import DbConfig, DbModule

@Module(
    imports=[
        DbModule.for_root(
            DbConfig(url="sqlite:///db.sqlite", models=[])
        ),
        # other modules...
    ]
)
class AppModule:
    ...
```

To load the config asynchronously, use `DbModule.for_root_async`:

```python
from typing import Annotated
from nestipy.common import Module
from nestipy.ioc import Inject
from nestipy_config import ConfigModule, ConfigService, ConfigOption
from nestipy_db import DbConfig, DbModule

async def get_db_config(config: Annotated[ConfigService, Inject()]):
    return DbConfig(
        url=config.get("DATABASE_URL"),
        models=[]
    )

@Module(
    imports=[
        ConfigModule.for_root(ConfigOption(), is_global=True),
        DbModule.for_root_async(
            factory=get_db_config,
            inject=[ConfigService]
        ),
        # other modules...
    ]
)
class AppModule:
    ...
```

## Note

Note that, you need to register all of your models inside `DbConfig(..., models=[])` or by importing `DbModule.for_feature(Model1, Model2)` in your current module.

## CLI

NestipyDB aliases Edgy CLI commands and adds support for model generation.
Instead of using `edgy`, use:

```bash
nestipy run db #follow edgy command
```

NestipyDB introduces a new model generation command:

```bash
nestipy run db new|g|gen|generate model_name module_name
```

* `module_name` is optional.
* If omitted, `model_name` will also be used as the `module_name`.
* The model will be created inside the specified module, or the module folder will be created if it doesn't exist.

## Support

Nestipy is an MIT-licensed open source project. It continues to grow thanks to support from the community.
If you'd like to contribute or sponsor, please \[read more here].

## Stay in Touch

* **Author** - [Tsiresy Mila](https://tsiresymila.vercel.app)

## License

Nestipy is [MIT licensed](LICENSE).
