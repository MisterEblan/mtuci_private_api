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

class GetScheduleError(Exception):
    """Ошибка при получении данных о расписании"""
    pass

class ParseError(Exception):
    """Ошибка парсинга"""
    pass

class HttpClientError(Exception):
    """Ошибка запроса HTTP-клиента"""
    pass
