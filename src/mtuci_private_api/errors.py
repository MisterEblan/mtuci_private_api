"""Кастомные ошибки и исключения"""

class AuthError(Exception):
    """Ошибка при аутентификации"""
    pass

class GetUserInfoError(Exception):
    """Ошибка при получении информации о пользователе"""
    pass

class GetAttendanceError(Exception):
    """Ошибка при получении данных о посещаемости"""
    pass
