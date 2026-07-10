import importlib

import pytest

MODULES = [
    "src.core.config",
    "src.core.logger",
    "src.usecases.search",
    "src.usecases.playback",
    "src.api.routers.search",
    "src.api.routers.playback",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_import_module(module_name):
    importlib.import_module(module_name)
