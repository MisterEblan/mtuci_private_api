import pytest
import json

from src.mtuci_private_api.http import HttpClient
from src.mtuci_private_api.attendance import AttendanceService
from src.mtuci_private_api.user.service import UserService
from src.mtuci_private_api.config import app_config
from src.mtuci_private_api.auth import AutoAuthService
from src.mtuci_private_api.models import User
from src.mtuci_private_api.http import HttpClient, BaseHttpClient
from src.mtuci_private_api.schedule import ScheduleService

from httpx import AsyncClient
from typing import Any

from .fixtures.attendance_http_client import fake_attendance_http_client
from .fixtures.user_http_client import fake_user_http_client
from .fixtures.schedule_http_client import fake_schedule_client

@pytest.fixture
def mtuci_login() -> str:
    assert (login := app_config.mtuci_login)

    return login

@pytest.fixture
def mtuci_password() -> str:
    assert (password := app_config.mtuci_password)

    return password

@pytest.fixture
def client() -> HttpClient:
    client = AsyncClient(
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        },
        # cookies=Cookies(),
        follow_redirects=True
    )

    return BaseHttpClient(client)

@pytest.fixture
def auth_service(
    mtuci_login: str,
    mtuci_password: str,
    client: BaseHttpClient
) -> AutoAuthService:
    return AutoAuthService(
        login=mtuci_login,
        password=mtuci_password,
        client=client
    )

@pytest.fixture
async def auth_client(
    auth_service: AutoAuthService
) -> HttpClient:
    await auth_service.auth()

    return BaseHttpClient(auth_service.client.session)

@pytest.fixture
async def no_auth_attendance_service(
        fake_attendance_http_client: HttpClient
) -> AttendanceService:
    service = AttendanceService(
        client=fake_attendance_http_client,
    )

    return service

@pytest.fixture
async def schedule_service(
    fake_schedule_client: HttpClient
) -> ScheduleService:
    return ScheduleService(
        client=fake_schedule_client,
        user_info=User(
            uid="",
            name="Unknown",
            group="БИК2404",
            speciality="",
            course="Второй",
            department="РиТ"
        )
    )


@pytest.fixture
async def user_service(
    fake_user_http_client: HttpClient
) -> UserService:
    return UserService(
        client=fake_user_http_client
    )

@pytest.fixture
def attendance_list() -> dict[str, Any]:
    with open(
        "tests/fixtures/attendance_list.json",
        "r",
        encoding="utf-8"
    ) as f:
        content = json.load(f)

    return content

@pytest.fixture
def skips_list() -> dict[str, Any]:
    with open(
        "tests/fixtures/skips_list.json",
        "r",
        encoding="utf-8"
    ) as f:
        content = json.load(f)

    return content

@pytest.fixture
def user_info() -> dict[str, Any]:
    with open(
        "tests/fixtures/user_info.json",
        "r",
        encoding="utf-8"
    ) as f:
        content = json.load(f)

    return content

@pytest.fixture
def timetable() -> dict[str, Any]:
    with open(
        "tests/fixtures/timetable.json",
        "r",
        encoding="utf-8"
    ) as f:
        content = json.load(f)

    return content
