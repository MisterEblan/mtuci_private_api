from typing import Any
from httpx import Response
import pytest
import json
from src.mtuci_private_api.attendance.http import (
    HttpClient,
    Method
)

class FakeHttpClient(
    HttpClient
):
    attendance_list_processor = "getArray_ArrayDicsiplinesStudentAttendance"
    skips_processor = "getData_ArrayScoreStudenLessonAttendance"
    async def request(
        self,
        method: Method,
        url: str,
        **kwargs: Any
    ) -> Response:
        body = kwargs.pop("body")
        processor = body.get("processor")


        if processor == self.attendance_list_processor:
            print("process: list")
            with open(
                "tests/fixtures/attendance_list.json",
                "r",
                encoding="utf-8"
            ) as f:
                content = json.load(f)

            response = Response(
                status_code=200,
                json=content
            )
            return response

        if processor == self.skips_processor:
            print("processor: skips")
            with open(
                "tests/fixtures/skips_list.json",
                "r",
                encoding="utf-8"
            ) as f:
                content = json.load(f)

            response = Response(
                status_code=200,
                content=json.dumps(content).encode("utf-8")
            )

            return response

        print("unknown processor - error")
        return Response(status_code=400)

@pytest.fixture
def fake_attendance_http_client() -> HttpClient:
    return FakeHttpClient()
