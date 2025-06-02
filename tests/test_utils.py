import pytest
from unittest.mock import patch, mock_open, MagicMock
import utils


@pytest.fixture
def sample_csv():
    return """name,age\nAlice,30\nBob,not_a_number\nCharlie,25\n"""


def sample_parser(row):
    return {"name": row["name"], "age": int(row["age"])}


def test_objects_from_csv_success_and_errors(sample_csv):
    logger = MagicMock()
    expected_objects = [
        {"name": "Alice", "age": 30},
        {"name": "Charlie", "age": 25}
    ]
    expected_errors = [
        {
            "row_num": 2,
            "error": "invalid literal for int() with base 10: 'not_a_number'",
            "row": {"name": "Bob", "age": "not_a_number"}
        }
    ]

    with patch("builtins.open", mock_open(read_data=sample_csv)):
        result_objects, result_errors = utils.objects_from_csv(
            "fake_path.csv", sample_parser, logger=logger
        )

    assert result_objects == expected_objects
    assert result_errors == expected_errors
    logger.error.assert_called_once()


def test_objects_from_csv_all_valid():
    valid_csv = """name,age\nAnna,22\nBen,40\n"""
    with patch("builtins.open", mock_open(read_data=valid_csv)):
        objects, errors = utils.objects_from_csv("dummy.csv", sample_parser)
    assert objects == [{"name": "Anna", "age": 22}, {"name": "Ben", "age": 40}]
    assert errors == []


def test_objects_from_csv_all_invalid():
    invalid_csv = """name,age\nFoo,abc\nBar,xyz\n"""
    logger = MagicMock()
    with patch("builtins.open", mock_open(read_data=invalid_csv)):
        objects, errors = utils.objects_from_csv("dummy.csv", sample_parser, logger)

    assert objects == []
    assert len(errors) == 2
    assert logger.error.call_count == 2
