import pytest
from unittest.mock import MagicMock, patch
from api import (
    add_objects,
    update_object,
    delete_object
)
from dataclasses import dataclass

@dataclass
class Dummy:
    id: int
    name: str


def test_add_objects_ok(fake_cursor):
    dummy = Dummy(id=1, name="test")
    with patch("api.insert_rows") as mock_insert, \
         patch("api.api_response") as mock_response:
        mock_insert.return_value = 1
        expected = {"success": True, "message": "Dummys added: 1"}
        mock_response.return_value = expected
        result = add_objects(fake_cursor, (dummy,), "Dummy", ["id", "name"], Dummy)
        assert result == expected


def test_add_objects_exception(fake_cursor):
    dummy = Dummy(id=1, name="test")
    with patch("api.insert_rows", side_effect=Exception("DB Error")), \
         patch("api.api_response") as mock_response:
        expected = {"success": False, "message": "Error adding Dummy: DB Error", "status_code": 500, "log_type": "error"}
        mock_response.return_value = expected
        result = add_objects(fake_cursor, (dummy,), "Dummy", ["id", "name"], Dummy)
        assert result == expected

# update_object 

def test_update_object_ok(fake_cursor):
    dummy = Dummy(id=1, name="updated")
    with patch("api.update_row") as mock_update, \
         patch("api.api_response") as mock_response, \
         patch("api.logger") as mock_logger:
        mock_update.return_value = 1
        expected = {"success": True, "message": "Dummy with id=1 updated"}
        mock_response.return_value = expected
        result = update_object(fake_cursor, dummy, "Dummys", ["name"], "id")
        assert result == expected


def test_update_object_not_found(fake_cursor):
    dummy = Dummy(id=1, name="nope")
    with patch("api.update_row", return_value=0), \
         patch("api.api_response") as mock_response:
        expected = {"success": False, "message": "Dummy not found", "status_code": 404, "log_type": "warning"}
        mock_response.return_value = expected
        result = update_object(fake_cursor, dummy, "Dummys", ["name"], "id")
        assert result == expected


def test_update_object_exception(fake_cursor):
    dummy = Dummy(id=1, name="err")
    with patch("api.update_row", side_effect=Exception("fail")), \
         patch("api.api_response") as mock_response, \
         patch("api.logger") as mock_logger:
        expected = {"success": False, "message": "Error updating Dummy: fail", "status_code": 500, "log_type": "error"}
        mock_response.return_value = expected
        result = update_object(fake_cursor, dummy, "Dummys", ["name"], "id")
        assert result == expected

# delete_object

def test_delete_object_ok(fake_cursor):
    with patch("api.delete_row", return_value=1), \
         patch("api.api_response") as mock_response, \
         patch("api.logger") as mock_logger:
        expected = {"success": True, "message": "Dummy with id=1 deleted"}
        mock_response.return_value = expected
        result = delete_object(fake_cursor, "Dummys", "id", 1)
        assert result == expected


def test_delete_object_not_found(fake_cursor):
    with patch("api.delete_row", return_value=0), \
         patch("api.api_response") as mock_response, \
         patch("api.logger") as mock_logger:
        expected = {"success": False, "message": "Dummy not found", "status_code": 404, "log_type": "warning"}
        mock_response.return_value = expected
        result = delete_object(fake_cursor, "Dummys", "id", 1)
        assert result == expected


def test_delete_object_exception(fake_cursor):
    with patch("api.delete_row", side_effect=Exception("fail")), \
         patch("api.api_response") as mock_response, \
         patch("api.logger") as mock_logger:
        expected = {"success": False, "message": "Error deleting Dummy: fail", "status_code": 500, "log_type": "error"}
        mock_response.return_value = expected
        result = delete_object(fake_cursor, "Dummys", "id", 1)
        assert result == expected
