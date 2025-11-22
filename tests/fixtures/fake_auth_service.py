from httpx import Response
import pytest
from src.mtuci_private_api.auth import AutoAuthService

class FakeAuthService(AutoAuthService):

    def __init__(self): 
        pass

    async def auth(self) -> Response:
        return Response(status_code=200)

@pytest.fixture
def fake_auth_service() -> FakeAuthService:
    return FakeAuthService()
