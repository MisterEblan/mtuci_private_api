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
