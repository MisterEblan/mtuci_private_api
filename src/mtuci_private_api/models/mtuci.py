"""Модели для данных из ЛК МТУСИ"""

from pydantic import BaseModel

class Attendance(BaseModel):
    """Посещаемость по предмету

    Attributes:
        subject_name: название предмета.
        attendance_percentage: процент посещений.
        skips: количество пропусков
    """
    uid: str | None = None
    subject_name: str
    attendance_percentage: float
    skips: int | None = None

class User(BaseModel):
    """Информация о студенте

    Attributes:
        uid: идентификатор.
        department: факультет.
        group: группа.
        course: курс (первый, второй и т.д.)
    """

    uid: str | None
    department: str
    group: str
    course: str
