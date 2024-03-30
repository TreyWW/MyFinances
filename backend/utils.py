from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient

cache: RedisCacheClient = cache

from backend.models import FeatureFlags

def get_feature_status(feature, should_use_cache=True):
    if should_use_cache:
        key = f"myfinances:feature_flag:{feature}"
        cached_value = cache.get(key)
        if cached_value:
            return cached_value

    value = FeatureFlags.objects.filter(name=feature).first()
    if value:
        if should_use_cache:
            cache.set(key, value.value, timeout=300)
        return value.value
    else:
        return False
