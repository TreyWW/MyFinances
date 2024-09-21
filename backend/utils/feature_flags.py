from backend.models import FeatureFlags
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient

cache: RedisCacheClient = cache


def get_feature_status(feature, should_use_cache=True):
    cache_key = f"myfinances:feature_flag:{feature}"

    if should_use_cache:
        cached_value = cache.get(cache_key, None)
        if cached_value:
            return cached_value

    value = FeatureFlags.objects.filter(name=feature).first()

    if should_use_cache:
        cache.set(cache_key, value.value, timeout=300)
    return value.value


def set_cache(key, value, timeout=300):
    cache.set(key, value, timeout=timeout)


def get_cache(key):
    return cache.get(key)
