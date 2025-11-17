import pytest
from mtuci_private_api.attendance import AttendanceService
from src.mtuci_private_api.config import app_config
from src.mtuci_private_api.auth import AuthService
from httpx import AsyncClient

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
        },
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
