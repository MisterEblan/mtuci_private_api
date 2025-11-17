from src.mtuci_private_api.attendance import AttendanceService
import pytest
import json

class TestAttendanceService:

    @pytest.mark.asyncio
    async def test_get_attendance(
        self,
        attendance_service: AttendanceService
    ):
        attendance = await attendance_service.get_attendance()

        print(
            attendance
        )

        assert attendance
