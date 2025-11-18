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
        attendance_service: AttendanceService
    ):
        attendance = await attendance_service.get_attendance()

        print(
            json.dumps(attendance, indent=2, ensure_ascii=False, default=dict)
        )

        assert attendance

    @pytest.mark.asyncio
    async def test_get_subject_skips(
        self,
        attendance_service: AttendanceService,
        subject_uid: str,
        subject_name: str
    ):
        skips = await attendance_service.get_subject_skips(
            subject_uid,
            subject_name
        )

        print("Skips:", skips)
        assert skips
