from httpx import Response
from src.mtuci_private_api.errors import GetAttendanceError
from src.mtuci_private_api.http.base import HttpClient
from src.mtuci_private_api.attendance import AttendanceService
from unittest.mock import AsyncMock
import pytest
import json

class TestAttendanceService:

    @pytest.fixture
    def subject_uid(self) -> str:
        return "5a134f6a-35d1-11ee-8400-6cb3115e8254"

    @pytest.fixture
    def subject_name(self) -> str:
        return "Основы работы с измерительной техникой"

    @pytest.mark.asyncio
    async def test_get_attendance(
        self,
        no_auth_attendance_service: AttendanceService
    ):
        attendance = await no_auth_attendance_service.get_attendance()

        print(
            json.dumps(attendance, indent=2, ensure_ascii=False, default=dict)
        )

        assert attendance

    async def test_get_attendance_fail(
        self,
    ):
        mock_response = AsyncMock(Response)
        mock_response.json.return_value = {"state": "bad"}

        mock_client = AsyncMock(HttpClient)
        mock_client.request.return_value = mock_response

        service = AttendanceService(mock_client)

        with pytest.raises(
            GetAttendanceError, match="Error parsing response"
        ):
            await service.get_attendance()
