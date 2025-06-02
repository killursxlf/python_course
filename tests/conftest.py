import pytest
from unittest.mock import MagicMock

@pytest.fixture
def fake_cursor():
    fake_cursor = MagicMock()
    fake_cursor.connection = fake_cursor
    return fake_cursor