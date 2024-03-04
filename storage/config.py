from toycommons.model.config import ConfigData
from .cached_dataclass import CachedDataclass


class Config(CachedDataclass):
    """
    Main global config. todo: reduce this into a default CachedDataClass within __init__
    """
    datacls = ConfigData

    @property
    def re_cache(self):
        return self.data.re_cache
