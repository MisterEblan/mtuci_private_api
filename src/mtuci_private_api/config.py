"""Конфигурация приложения"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from yaml import safe_load
import logging.config

class AppConfig(BaseSettings):
    """Конфигурация"""
    mtuci_login: str
    mtuci_password: str
    mtuci_url: str = "https://lk.mtuci.ru"

    user_uid: str
    user_dep: str
    user_group: str
    user_spec:   str
    user_course: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8",
    )

def setup_logging_config() -> None:
    """Загрузка конфига для логирования"""

    path = Path("./logging_config.yaml")

    try:

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as f:
            config = safe_load(f)

        logging.config.dictConfig(config)
    except Exception as err:
        print("Error loading configuration for logging:", err)
        print("Using basic configuration")

        logging.basicConfig()

app_config = AppConfig()
setup_logging_config()
