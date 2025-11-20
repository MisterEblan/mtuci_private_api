"""Парсеры для посещаемости"""

from .attendance_list import AttendanceListParser
from .skips import SkipsParser
from .subject_params import SubjectParamsParser

__all__ = [
    "AttendanceListParser",
    "SkipsParser",
    "SubjectParamsParser"
]
