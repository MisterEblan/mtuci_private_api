"""Парсер для списка посещаемости"""

from typing import Any

from ...errors import ParseError
from ...models.mtuci import Attendance
from .base import Parser

class AttendanceListParser(
    Parser[dict[str, Any], list[Attendance]]
):
    """Парсер для списка посещаемости"""

    def validate(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> bool:

        if obj.get("state") != "ok":
            return False
        
        data = obj.get("data", {})

        if not data.get("Ответ", []):
            return False

        return True

    def parse(
        self,
        obj: dict[str, Any],
        **kwargs: Any
    ) -> list[Attendance]:
        if not self.validate(obj):
            raise ParseError("Object is not valid")

        data = obj.get("data", {}).get("Ответ", [])
        data = data[0].get("Содержимое", {})

        table = data.get("ТаблицаДанных", [])

        result = []

        for subject in table:
            name = subject.get("ПредставлениеПары", "")
            percent = float(
                subject.get("ПроцентПосещений", "0,0")
                .replace(",", ".")
            )
            uid = None
            if command := subject.get("data", {}).get("command", []):
                uid = (
                    command[0].get("ПараметрыКоманды", {})
                    .get("Дисциплина", {})
                    .get("uid", None)
                )

            attendance = Attendance(
                uid=uid,
                subject_name=name,
                attendance_percentage=percent,
            )

            result.append(attendance)

        return result
