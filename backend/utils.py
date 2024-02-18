# import boto3
# from appconfig_helper import AppConfigHelper
#
# from settings.helpers import get_var
#
#
# class AppConfig:
#     def __init__(self):
#         self.ENABLED = get_var("AWS_FEATURE_FLAGS_ENABLED")
#         self.APPLICATION = get_var("AWS_FEATURE_FLAGS_APPLICATION")
#         self.ENVIRONMENT = get_var("AWS_FEATURE_FLAGS_ENVIRONMENT")
#         self.PROFILE = get_var("AWS_FEATURE_FLAGS_PROFILE")
#         self.UPDATE_CHECK_INTERVAL = get_var(
#             "AWS_FEATURE_FLAGS_UPDATE_CHECK_INTERVAL", default=45
#         )
#
#         if self.ENABLED:
#             print("[BACKEND] Feature flags enabled", flush=True)
#             print(f"""Using these variables:
#                 APPLICATION: {self.APPLICATION}
#                 ENVIRONMENT: {self.ENVIRONMENT}
#                 PROFILE: {self.PROFILE}
#                 UPDATE_CHECK_INTERVAL: {self.UPDATE_CHECK_INTERVAL}
#             """, flush=True)
#             session = boto3.session.Session(
#                 aws_access_key_id=get_var("AWS_FEATURE_FLAGS_ACCESS_KEY_ID"),
#                 aws_secret_access_key=get_var("AWS_FEATURE_FLAGS_SECRET_ACCESS_KEY"),
#                 region_name=get_var("AWS_FEATURE_FLAGS_REGION_NAME"),
#             )
#             self.appconfig: AppConfigHelper = AppConfigHelper(
#                 self.APPLICATION,
#                 self.ENVIRONMENT,
#                 self.PROFILE,
#                 self.UPDATE_CHECK_INTERVAL,  # minimum interval between update checks (SECONDS)
#                 fetch_on_init=True,
#                 fetch_on_read=True,
#                 session=session
#             )
#             print("[BACKEND] Got past app config init... Attempting test", flush=True)
#             print(f"[BACKEND] {self.appconfig.raw_config}", flush=True)
#             print(self.get_feature_status("areSignupsEnabled"), flush=True)
#             print("[BACKEND] Feature flags status ^^", flush=True)
#         else:
#             print(
#                 "[BACKEND] Feature flags disabled; using mock feature flags", flush=True
#             )
#
#             class AppConfigMock:
#                 config = {"areSignupsEnabled": {"enabled": True}}
#
#             self.appconfig = AppConfigMock()
#
#     def update_feature_flags(self):
#         return self.appconfig.update_config() if self.ENABLED else False
#
#     def get_feature_status(self, feature):
#         return self.appconfig.config.get(feature, {}).get("enabled", False)
#
#
# appconfig = AppConfig()
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient

cache: RedisCacheClient = cache

from backend.models import FeatureFlags


def get_feature_status(feature):
    key = f"myfinances:feature_flag:{feature}"
    cached_value = cache.get(key)
    if cached_value:
        return cached_value

    value = FeatureFlags.objects.filter(name=feature).first()
    if value:
        cache.set(key, value.value, timeout=300)
        return value.value
    else:
        return False
