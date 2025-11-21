"""Библиотека для работы с личным кабинетом МТУСИ"""

from .mtuci import Mtuci
from .models import (
        User,
        Attendance,
        Schedule,
        Lesson,
        LessonType
)
from .errors import (
    AuthError,
    GetAttendanceError,
    GetScheduleError,
    GetUserInfoError,
    ParseError
)

__all__ = [
    "Mtuci",
    "User",
    "Attendance",
    "Schedule",
    "Lesson",
    "LessonType",
    "AuthError",
    "GetAttendanceError",
    "GetScheduleError",
    "GetUserInfoError",
    "ParseError"
]
