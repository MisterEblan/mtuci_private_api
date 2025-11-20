from src.mtuci_private_api.attendance import AttendanceService
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
