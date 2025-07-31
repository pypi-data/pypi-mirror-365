import importlib
import importlib.util
import os
import sys
from importlib.machinery import ModuleSpec
from typing import Any, Callable, Optional

from ml_collections import FieldReference


def get_class_path(cls: Callable) -> str:
    """
    Returns the full path of a class as a string.

    Copied from https://github.com/Farama-Foundation/HighwayEnv
    """
    return cls.__module__ + "." + cls.__qualname__


def class_from_path(path: str) -> Callable:
    """
    Returns a class object from its full path.
    The path should be in the format 'module.ClassName'.

    Copied from https://github.com/Farama-Foundation/HighwayEnv
    """
    module_name, class_name = path.rsplit(".", 1)
    class_object = getattr(importlib.import_module(module_name), class_name)
    return class_object


def instantiate_object_from_config(config: dict) -> Callable:
    """
    Instantiates a class from a configuration dictionary.
    The dictionary must contain a 'type' key with the full class path.
    """
    assert "type" in config, "Config must contain 'type' key"
    class_path = config["type"]
    params = {k: v for k, v in config.items() if not k == "type"}
    class_object = class_from_path(class_path)
    return class_object(**params)


def load_config(*, config_path: str, overrides: Optional[list[str]] = None) -> dict:
    """
    Load a Python configuration file and extract its variables into a dictionary.
    Variables that start with an underscore, callable objects, and modules are filtered out.
    """
    config_path = os.path.abspath(config_path)
    spec = importlib.util.spec_from_file_location("user_config", config_path)
    assert isinstance(spec, ModuleSpec), "Failed to load module spec"

    config = importlib.util.module_from_spec(spec)
    sys.modules["user_config"] = config
    spec.loader.exec_module(config)

    config = vars(config)
    _update_config_with_overrides(config=config, overrides=overrides)

    # Extract variables: filter out built-ins and modules
    config_dict = _resolve_config_dict(config)
    return config_dict


def _resolve_config_dict(config: dict) -> dict:
    def _resolve_value(value: Any) -> Any:
        if isinstance(value, dict):
            return _resolve_config_dict(value)
        elif isinstance(value, list):
            return [_resolve_value(item) for item in value]
        elif isinstance(value, tuple):
            return tuple(_resolve_value(item) for item in value)
        elif isinstance(value, set):
            return {_resolve_value(item) for item in value}
        elif isinstance(value, FieldReference):
            return value.get()
        return value

    config_dict = {
        key: _resolve_value(value)
        for key, value in config.items()
        if not key.startswith("_")
        and not callable(value)
        and not isinstance(value, type(sys))
    }
    return config_dict


def _update_config_with_overrides(
    *, config: dict, overrides: Optional[list[str]]
) -> dict:
    """
    Update the configuration dictionary with command line overrides.
    Each override should be in the format 'key=value'.
    e.g. "--override port=9090 --override config.batch_size=32"
    """
    if overrides:
        for item in overrides:
            key, value = item.split("=", 1)
            _set_nested(config, key, value)
    return config


def _set_nested(config, var_path, value):
    """
    Set a nested value in config given a dotted path (e.g., my_dict.name).
    """
    keys = var_path.split(".")
    obj = config
    for key in keys[:-1]:
        obj = getattr(obj, key) if hasattr(obj, key) else obj[key]

    # Convert value to appropriate type
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    else:
        try:
            value = int(value)
        except ValueError:
            try:
                value = float(value)
            except ValueError:
                pass

    # handle FieldReference overrides
    if isinstance(obj[keys[-1]], FieldReference):
        obj[keys[-1]].set(value)
    else:
        obj[keys[-1]] = value
