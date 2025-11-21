from httpx import Response
from ....parsers import Parser
from ....errors import ParseError
from typing import Any

class CookieParser(
    Parser[Response, list[int]]
):

    def validate(
        self,
        obj: Response,
        **kwargs: Any
    ) -> bool:
        raw = obj.cookies.get("__js_p_")

        if not raw:
            return False

        return True

    def parse(
            self,
            obj: Response,
            **kwargs: Any
    ) -> list[int]:

        if not self.validate(obj):
            raise ParseError(f"Invalid object: {obj.cookies}")

        raw = obj.cookies.get("__js_p_", "")

        raw_splitted = raw.split(",")

        raw_splitted = list(map(int, raw_splitted))

        return raw_splitted
