
import pytest

from speed import create_app
from speed.config import TestConfig


@pytest.fixture(scope="session")
def app(request):
    """Test session-wide test `Flask` application."""
    app = create_app(TestConfig)
    return app