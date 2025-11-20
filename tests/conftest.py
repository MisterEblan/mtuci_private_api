import pytest
import json

from src.mtuci_private_api.http import HttpClient, BaseHttpClient
from src.mtuci_private_api.attendance import AttendanceService
from src.mtuci_private_api.user.service import UserService
from src.mtuci_private_api.config import app_config
from src.mtuci_private_api.auth import AutoAuthService
from src.mtuci_private_api.models import User

from httpx import AsyncClient
from os import getenv
from typing import Any

from .fixtures.attendance_http_client import fake_attendance_http_client

@pytest.fixture
def mtuci_login() -> str:
    assert (login := app_config.mtuci_login)

    return login

@pytest.fixture
def mtuci_password() -> str:
    assert (password := app_config.mtuci_password)

    return password

@pytest.fixture
def client() -> AsyncClient:
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

    return client

@pytest.fixture
def auth_service(
    mtuci_login: str,
    mtuci_password: str,
    client: AsyncClient
) -> AutoAuthService:
    return AutoAuthService(
        login=mtuci_login,
        password=mtuci_password,
        client=client
    )

@pytest.fixture
async def auth_client(
    auth_service: AutoAuthService
) -> AsyncClient:
    await auth_service.auth()

    return auth_service.client

@pytest.fixture
async def no_auth_attendance_service(
        fake_attendance_http_client: HttpClient
) -> AttendanceService:
    service = AttendanceService(
        client=fake_attendance_http_client,
    )

    return service


@pytest.fixture
async def user_service(
        auth_client: AsyncClient
) -> UserService:
    return UserService(
        client=auth_client
    )

@pytest.fixture
def user() -> User:
    uid = getenv("USER_UID", "")
    dep = getenv("USER_DEP", "")
    group = getenv("USER_GROUP", "")
    course = getenv("USER_COURSE", "")
    spec   = getenv("USER_SPEC", "")

    return User(
        uid=uid,
        department=dep,
        group=group,
        course=course,
        speciality=spec
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
