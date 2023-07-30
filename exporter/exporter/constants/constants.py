import logging


class EnvironmentVariableKeys():
    # prometheus_exporter configs
    EXPORTER_PORT_KEY = "EXPORTER_PORT"
    EXPORTER_LOG_LEVEL_KEY = "EXPORTER_LOG_LEVEL"
    EXPORTER_BIND_HOST_KEY = "EXPORTER_BIND_HOST"
    EXPORTER_NAMESPACE_KEY = "EXPORTER_NAMESPACE"

    # application env configs
    APP_CONFIG_FILE_KEY = "CONFIG_FILE"
    ACCOUNT_USERNAME_KEY = "ACCOUNT_USERNAME"
    ACCOUNT_PASSWORD_KEY = "ACCOUNT_PASSWORD"


class LogLevelOptions():
    # Logging Options
    log_level_options = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARN,
        "ERROR": logging.ERROR
    }


class TimeConstants():
    # reauthenticate every 15 min
    authentication_duration_min = 15
