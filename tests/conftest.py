import pytest
from src.mtuci_private_api.attendance import AttendanceService
from src.mtuci_private_api.user.service import UserService
from src.mtuci_private_api.config import app_config
from src.mtuci_private_api.auth import AuthService
from src.mtuci_private_api.models import User
from httpx import AsyncClient, Cookies
from os import getenv

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
) -> AuthService:
    return AuthService(
        login=mtuci_login,
        password=mtuci_password,
        client=client
    )

@pytest.fixture
async def auth_client(
        auth_service: AuthService
) -> AsyncClient:
    await auth_service.auth()

    return auth_service.client

@pytest.fixture
async def attendance_service(
    auth_client: AsyncClient
) -> AttendanceService:
    return AttendanceService(
        client=auth_client
    )

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
