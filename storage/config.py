from toycommons.model.config import ConfigData
from .cached_dataclass import CachedDataclass


class Config(CachedDataclass):
    datacls = ConfigData

    @property
    def re_cache(self):
        return self.data.re_cache
