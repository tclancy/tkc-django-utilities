from django.conf import settings
from django.core.cache import cache


class SmartCache(object):
    """
    Despite the name, this is pretty dumb, just a wrapper to Django's
    cache get/ set that respects our settings.USE_CACHE value to save
    repetitive code
    """
    @classmethod
    def get(cls, key, default=None):
        if not settings.USE_CACHE:
            return cache.get(key, default)
        return default

    @classmethod
    def set(cls, key, value, time_in_seconds=settings.DEFAULT_CACHE_TIMEOUT):
        if settings.USE_CACHE:
            cache.set(key, value, time_in_seconds)

    @classmethod
    def delete(cls, key):
        "Always do this, regardless of setting"
        cache.delete(key)