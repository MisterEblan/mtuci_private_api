"""Конфигурация приложения"""

from pydantic_settings import BaseSettings, SettingsConfigDict

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

app_config = AppConfig()
