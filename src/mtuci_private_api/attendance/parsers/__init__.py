"""Парсеры ответов"""

from .attendance_list import AttendanceListParser
from .skips import SkipsParser
from .subject_params import SubjectParamsParser
from .base import Parser

__all__ = [
    "AttendanceListParser",
    "SkipsParser",
    "SubjectParamsParser",
    "Parser"
]
