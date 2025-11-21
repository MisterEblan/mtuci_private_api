from typing import Any
from ....http import RequestFactory

class LoginRequestFactoryV1(RequestFactory):

    def create(
        self,
        **kwargs: Any
    ) -> dict[str, Any]:
        try:
            login = kwargs.pop("login")
            password = kwargs.pop("password")

            return {
                "username": login,
                "password": password,
                "rememberMe": "on",
                "credentialId": ""
            }

        except KeyError as err:
            raise ValueError("Login or password not provided") from err
