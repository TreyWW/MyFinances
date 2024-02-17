from appconfig_helper import AppConfigHelper

from settings.helpers import get_var

ENABLED = get_var("AWS_FEATURE_FLAGS_ENABLED")
APPLICATION = get_var("AWS_FEATURE_FLAGS_APPLICATION")
ENVIRONMENT = get_var("AWS_FEATURE_FLAGS_ENVIRONMENT")
PROFILE = get_var("AWS_FEATURE_FLAGS_PROFILE")
UPDATE_CHECK_INTERVAL = get_var("AWS_FEATURE_FLAGS_UPDATE_CHECK_INTERVAL", default=45)

if ENABLED:
    appconfig = AppConfigHelper(
        APPLICATION,
        ENVIRONMENT,
        PROFILE,
        UPDATE_CHECK_INTERVAL  # minimum interval between update checks (SECONDS)
    )
else:
    appconfig = {
        "config": {
            "areSignupsEnabled": {
                "enabled": True
            }
        }
    }


def update_feature_flags():
    return appconfig.update_config() if enabled else False


if update_feature_flags():
    print("[BACKEND] There has been changes to APP_CONFIG. New config will now be in place.")
