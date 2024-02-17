from appconfig_helper import AppConfigHelper

from settings.helpers import get_var


class AppConfig:
    def __init__(self):
        self.ENABLED = get_var("AWS_FEATURE_FLAGS_ENABLED")
        self.APPLICATION = get_var("AWS_FEATURE_FLAGS_APPLICATION")
        self.ENVIRONMENT = get_var("AWS_FEATURE_FLAGS_ENVIRONMENT")
        self.PROFILE = get_var("AWS_FEATURE_FLAGS_PROFILE")
        self.UPDATE_CHECK_INTERVAL = get_var("AWS_FEATURE_FLAGS_UPDATE_CHECK_INTERVAL", default=45)

        if self.ENABLED:
            print("[BACKEND] Feature flags enabled", flush=True)
            self.appconfig: AppConfigHelper = AppConfigHelper(
                self.APPLICATION,
                self.ENVIRONMENT,
                self.PROFILE,
                self.UPDATE_CHECK_INTERVAL  # minimum interval between update checks (SECONDS)
            )
        else:
            print("[BACKEND] Feature flags disabled; using mock feature flags", flush=True)
            class AppConfigMock:
                config = {
                    "areSignupsEnabled": {
                        "enabled": True
                    }
                }

            self.appconfig = AppConfigMock()

    def update_feature_flags(self):
        return self.appconfig.update_config() if self.ENABLED else False

    def get_feature_status(self, feature):
        return self.appconfig.config.get(feature, {}).get("enabled", False)


appconfig = AppConfig()
