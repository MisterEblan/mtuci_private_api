import pytest
from src.mtuci_private_api.http.request_factory import RequestFactory
from src.mtuci_private_api.attendance.request_factory import ProcessorRequestFactory

class TestAttendanceRequestFactories:

    @pytest.fixture
    def processor_factory(self) -> RequestFactory:
        return ProcessorRequestFactory()

    def test_factory_fail(
        self,
        processor_factory: RequestFactory
    ):
        with pytest.raises(ValueError):
            processor_factory.create()
