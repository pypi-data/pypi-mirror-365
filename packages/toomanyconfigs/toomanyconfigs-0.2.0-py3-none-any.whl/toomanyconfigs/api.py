from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Optional

import httpx
from loguru import logger as log
from .core import TOMLConfig

@dataclass
class HeadersConfig(TOMLConfig):
    """Configuration for HTTP headers"""
    authorization: str = "Bearer ${API_KEY}"
    accept: str = "application/json"

    def to_headers(self) -> Dict[str, str]:
        """Convert config to headers dictionary"""
        headers = {}
        if self.authorization:
            headers["Authorization"] = self.authorization
        if self.accept:
            headers["Accept"] = self.accept
        return headers

@dataclass
class RoutesConfig(TOMLConfig):
    """Configuration for URLs and routes"""
    base: str = ""
    routes: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not self._validate(): log.error("[Routes] Validation failed")

    def _validate(self) -> bool:
        try:
            if not isinstance(self.base, str) or not isinstance(self.routes, dict):
                raise TypeError
            for k, v in self.routes.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError
        except Exception as e:
            log.error(f"[Routes] Invalid routes: {e}")
            return False
        return True

    def __getitem__(self, key: str) -> str:
        if key not in self.routes:
            raise KeyError(f"Missing route: {key}")
        return self.base + self.routes[key]

@dataclass
class VarsConfig(TOMLConfig):
    """Configuration for variable substitution"""
    api_key: str = None

@dataclass
class APIConfig(TOMLConfig):
    """Main API configuration with sub-configs"""
    headers: HeadersConfig = field(default_factory=HeadersConfig)
    routes: RoutesConfig = field(default_factory=RoutesConfig)
    vars: VarsConfig = field(default_factory=VarsConfig)

    def __post_init__(self):
        super().__post_init__()
        # Initialize sub-configs if they're None
        if self.headers is None:
            self.headers = HeadersConfig()
        if self.routes is None:
            self.routes = RoutesConfig()
        if self.vars is None:
            self.vars = VarsConfig()

    def apply_variable_substitution(self):
        """Apply variable substitution to string fields"""
        vars_dict = self.vars._serialize_to_dict()

        # Apply to headers
        for field_name in self.headers._get_config_fields():
            value = getattr(self.headers, field_name)
            if isinstance(value, str):
                for var_key, var_val in vars_dict.items():
                    if var_val:
                        value = value.replace(f"${{{var_key.upper()}}}", str(var_val))
                        value = value.replace(f"${var_key.upper()}", str(var_val))
                setattr(self.headers, field_name, value)

        # Apply to URL base
        if self.routes.base:
            for var_key, var_val in vars_dict.items():
                if var_val:
                    self.routes.base = self.routes.base.replace(f"${{{var_key.upper()}}}", str(var_val))
                    self.routes.base = self.routes.base.replace(f"${var_key.upper()}", str(var_val))

@dataclass
class Headers:
    """Container for HTTP headers used in outgoing API requests."""
    index: Dict[str, str]
    accept: Optional[str] = None

    def __post_init__(self):
        self.accept = self.accept or "application/json"
        self.index["Accept"] = self.accept
        for k, v in self.index.items():
            setattr(self, k.lower().replace("-", "_"), v)
        if not self._validate():
            log.error("[Headers] Validation failed")

    def _validate(self) -> bool:
        try:
            if not isinstance(self.index, dict):
                raise TypeError
            for k, v in self.index.items():
                if not isinstance(k, str) or not isinstance(v, str):
                    raise ValueError
        except Exception as e:
            log.error(f"[Headers] Invalid headers: {e}")
            return False
        return True

    @cached_property
    def as_dict(self):
        return self.index

class _API:
    def __init__(self, config: APIConfig | Path = None):
        if isinstance(config, APIConfig):
            self.config = config
        elif isinstance(config, Path) or config is None:
            self.config = APIConfig.create(config)
        else:
            raise TypeError("Config must be 'APIConfig', Path, or None")
        self.config.apply_variable_substitution()

@dataclass
class Response:
    status: int
    method: str
    headers: dict
    body: Any

class Receptionist(_API):
    cache: dict[str | SimpleNamespace] = {}

    def __init__(self, config: APIConfig | Path | None = None):
        _API.__init__(self, config)

    async def api_request(self,
                          method: str,
                          route: str,
                          append: str = "",
                          format: dict = None,
                          force_refresh: bool = False,
                          append_headers: dict = None,
                          override_headers: dict = None,
                          **kw
                          ) -> Response:
        try:
            path = self.config.routes[route]
        except KeyError:
            path = route

        if format:
            path = path.format(**format)
        if append:
            path += append

        if override_headers:
            headers = override_headers
        else:
            headers = self.config.headers.to_headers()
            if append_headers:
                for k in append_headers:
                    headers[k] = append_headers[k]

        log.debug(f"{self}: Attempting request to API:\n  - method={method}\n  - headers={headers}\n  - path={path}")

        if not force_refresh:
            if path in self.cache:
                cache: Response = self.cache[path]
                log.debug(f"{self}: Found cache containing same route\n  - cache={cache}")
                if cache.method is method:
                    log.debug(
                        f"{self}: Cache hit for API Request:\n  - request_path={path}\n  - request_method={method}")
                    return self.cache[path]
                else:
                    log.warning(
                        f"{self}: No match! Cache was {cache.method}, while this request is {method}! Continuing...")

        async with httpx.AsyncClient(headers=headers) as client:
            response = await client.request(method.upper(), path, **kw)

            try:
                content_type = response.headers.get("Content-Type", "")
                if "json" in content_type:
                    content = response.json()
                else:
                    content = response.text
            except Exception as e:
                content = response.text  # always fallback
                log.warning(f"{self}: Bad response decode → {e} | Fallback body: {content}")

            out = Response(
                status=response.status_code,
                method=method,
                headers=dict(response.headers),
                body=content,
            )

            self.cache[path] = out
            return self.cache[path]

    async def api_get(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("get", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    async def api_post(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("post", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    async def api_put(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("put", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

    async def api_delete(self, route, append=None, format=None, force_refresh=False, append_headers=None, **kw):
        return await self.api_request("delete", route, append=append, format=format, force_refresh=force_refresh,
                                      append_headers=append_headers, **kw)

API = Receptionist

