REPR = "[TooManyConfigs]"
ACTIVE_CFGS = {}
from .core import TOMLConfig as TOMLDataclass
from .api import API, APIConfig, HeadersConfig, RoutesConfig, VarsConfig

