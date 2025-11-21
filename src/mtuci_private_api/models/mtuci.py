"""Модели для данных из ЛК МТУСИ"""

from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class Attendance(BaseModel):
    """Посещаемость по предмету

    Attributes:
        subject_name: название предмета.
        attendance_percentage: процент посещений.
        skips: количество пропусков
    """
    uid:                   str | None = None
    subject_name:          str
    attendance_percentage: float
    skips:                 int | None = None

class User(BaseModel):
    """Информация о студенте

    Attributes:
        uid: идентификатор.
        department: факультет.
        group: группа.
        course: курс (первый, второй и т.д.).
        speciality: специальность.
    """
    uid:        str | None
    name:       str
    department: str
    group:      str
    course:     str
    speciality: str

class LessonType(str, Enum):
    """Перечисление типов занятий"""
    LECTURE     = "Лекция"
    PRACTICE    = "Практическое занятие"
    LAB         = "Лабораторная работа"
    CREDIT      = "Зачёт"
    DIFF_CREDIT = "Дифференцированный зачет"
    EXAM        = "Экзамен"

class Lesson(BaseModel):
    """Предмет в расписании

    Attributes:
        name:       название предмета.
        type_:      тип занятия.
        is_retake:  является ли пересдачей.
        teachers:   преподаватели.
        audience:   аудитория.
        start_time: начало занятия.
        end_time:   окончание занятия.
    """
    name:       str
    type_:      LessonType
    is_retake:  bool
    teachers:   list[str]
    audience:   list[str]
    start_time: datetime
    end_time:   datetime

class Schedule(BaseModel):
    """Расписание на день"""
    date: datetime
    lessons: list[Lesson]
