import pytest
from typing import Any

from httpx import Response
from src.mtuci_private_api.http import HttpClient, Method

class FakeUserHttpClient(
    HttpClient
):

    async def request(
        self,
        method: Method,
        url: str,
        **kwargs: Any
    ) -> Response:
        with open(
            "tests/fixtures/user_info.json",
            "rb",
        ) as f:
            content = f.read()

        return Response(
            status_code=200,
            content=content,
        )

@pytest.fixture
def fake_user_http_client() -> HttpClient:
    return FakeUserHttpClient()
