"""Модуль для работы с аутентификацией"""

from .service_v1 import AuthServiceV1
from .service_v2 import AuthServiceV2
from .auto import AutoAuthService

__all__ = [
    "AuthServiceV1",
    "AuthServiceV2",
    "AutoAuthService"
]
