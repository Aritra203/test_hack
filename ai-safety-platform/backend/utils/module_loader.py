from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType


def load_module_from_path(module_name: str, module_path: Path) -> ModuleType:
    spec = spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to create import spec for module at {module_path}.")

    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached

    module = module_from_spec(spec)
    # Python 3.13 dataclass/type evaluation expects the module to be present in sys.modules.
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
