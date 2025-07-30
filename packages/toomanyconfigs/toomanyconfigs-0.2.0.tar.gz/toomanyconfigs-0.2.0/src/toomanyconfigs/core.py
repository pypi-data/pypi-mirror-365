import time
from dataclasses import dataclass, field
from typing import Dict, Any, Type, get_type_hints, Union

import pyperclip
import toml
from loguru import logger as log
from pathlib import Path
from . import ACTIVE_CFGS, REPR

@dataclass
class TOMLConfig:
    """Base class for TOML-based configuration with interactive setup and sub-config support"""

    def __post_init__(self):
        self._cwd = None
        self._path = None
        self._parent = None

    @classmethod
    def create(cls, source: Union[Path, 'TOMLConfig'] = None, **kwargs):
        """Create configuration from TOML file or existing config instance"""
        # If source is already a TOMLConfig instance, set it as parent
        if isinstance(source, TOMLConfig):
            inst = cls()
            inst._parent = source
            for kwarg in kwargs:
                setattr(inst, kwarg, kwargs.get(kwarg))
            return inst

        # Otherwise treat as Path and load from TOML
        inst = cls()
        for kwarg in kwargs:
            setattr(inst, kwarg, kwargs.get(kwarg))

        if source:
            inst._cwd = source.parent
            inst._path = source
            path = inst._path
        else:
            inst._cwd = Path.cwd()
            name = inst.__repr__().split("(")[0].lower()
            inst._path = Path.cwd() / (name + ".toml")
            path = inst._path

        if not inst._path.exists():
            log.warning(f"{REPR}: Config file not found at {path}, creating new one")
            path.touch(exist_ok=True)
            inst._prompt_all_fields()
            inst.write()
            return inst

        data = inst.read()
        inst._load_from_data(data)

        missing_fields = inst._get_missing_fields()
        if missing_fields:
            log.info(f"{inst}: Missing fields detected: {missing_fields}")
            inst._prompt_missing_fields(missing_fields)
            inst.write()

        return inst

    def _load_from_data(self, data):
        """Load data into instance fields, handling sub-configs"""
        type_hints = get_type_hints(self.__class__)

        for field_name in self._get_config_fields():
            if field_name not in data:
                continue

            field_type = type_hints.get(field_name)
            field_value = data[field_name]

            # Check if this field is a TOMLConfig subclass
            if self._is_toml_config_subclass(field_type):
                # Create instance of the sub-config
                sub_config = field_type()
                sub_config._load_from_data(field_value)
                setattr(self, field_name, sub_config)
                log.debug(f"{self}: Loaded sub-config {field_name}")
            else:
                setattr(self, field_name, field_value)
                log.debug(f"{self}: Loaded {field_name} from config")

    def _is_toml_config_subclass(self, field_type) -> bool:
        """Check if a type is a TOMLConfig subclass"""
        try:
            return (isinstance(field_type, type) and
                   issubclass(field_type, TOMLConfig) and
                   field_type != TOMLConfig)
        except TypeError:
            return False

    def _get_config_fields(self):
        """Get all non-private fields from dataclass"""
        return [name for name in self.__dataclass_fields__ if not name.startswith('_')]

    def _get_missing_fields(self):
        """Get fields that are None or empty, including sub-configs"""
        missing = []
        type_hints = get_type_hints(self.__class__)

        for name in self._get_config_fields():
            field_value = getattr(self, name)
            field_type = type_hints.get(name)

            if field_value is None:
                missing.append(name)
            elif self._is_toml_config_subclass(field_type) and hasattr(field_value, '_get_missing_fields'):
                # Check sub-config for missing fields
                sub_missing = field_value._get_missing_fields()
                if sub_missing:
                    missing.extend([f"{name}.{sub_field}" for sub_field in sub_missing])

        return missing

    def _prompt_all_fields(self):
        """Prompt for all configuration fields, including sub-configs"""
        type_hints = get_type_hints(self.__class__)

        for field_name in self._get_config_fields():
            field_type = type_hints.get(field_name)

            if self._is_toml_config_subclass(field_type):
                # Initialize sub-config and prompt for its fields
                if getattr(self, field_name) is None:
                    setattr(self, field_name, field_type())
                sub_config = getattr(self, field_name)
                log.info(f"{self}: Configuring sub-section '{field_name}'")
                sub_config._prompt_all_fields()
            else:
                if getattr(self, field_name) is None:
                    self._prompt_field(field_name)

    def _prompt_missing_fields(self, missing_fields):
        """Prompt for specific missing fields, handling sub-config notation"""
        for field_path in missing_fields:
            if '.' in field_path:
                # Handle sub-config field (e.g., "headers.authorization")
                parts = field_path.split('.', 1)
                sub_config_name, sub_field = parts
                sub_config = getattr(self, sub_config_name)
                if sub_config:
                    sub_config._prompt_field(sub_field)
            else:
                self._prompt_field(field_path)

    def _prompt_field(self, field_name):
        """Prompt user for a single field value"""
        time.sleep(1)
        prompt = f"{self}: Enter value for '{field_name}' (or press Enter to paste from clipboard): "
        user_input = input(prompt).strip()

        if not user_input:
            user_input = pyperclip.paste()
            log.debug(f"{self}: Using clipboard value for {field_name}")

        setattr(self, field_name, user_input)
        time.sleep(1)
        log.success(f"{self}: Set {field_name}")

    def write(self):
        """Write configuration to TOML file, handling sub-configs"""
        if not self._path:
            raise ValueError("No path set for configuration file")

        config_data = self._serialize_to_dict()

        log.debug(f"{REPR}: Writing config to {self._path}")
        with self._path.open('w') as f:
            toml.dump(config_data, f)

    def _serialize_to_dict(self) -> Dict[str, Any]:
        """Serialize config to dictionary, handling sub-configs"""
        type_hints = get_type_hints(self.__class__)
        config_data = {}

        for name in self._get_config_fields():
            field_value = getattr(self, name)
            field_type = type_hints.get(name)

            if field_value is None:
                continue

            if self._is_toml_config_subclass(field_type):
                # Serialize sub-config
                config_data[name] = field_value._serialize_to_dict()
            else:
                config_data[name] = field_value

        return config_data

    def read(self):
        """Read configuration from TOML file"""
        if not self._path or not self._path.exists():
            return {}

        log.debug(f"{REPR} Reading config from {self._path}")
        with self._path.open('r') as f:
            return toml.load(f)
