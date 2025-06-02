import pytest
from validator import validate_list, validate_full_name, validate_account_number, validate_field_value, validate_amount
from dataclasses import dataclass

@dataclass
class Fuu:
    id: int
    name: str
    
    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Name must be a non-empty string")

def test_validate_list():
    valid_data = [
        {"id": 1, "name": "Test1"},
        {"id": 2, "name": "Test2"}
    ]
    
    invalid_data = [
        {"id": 3, "name": ""},
        {"id": 4, "name": None}
    ]
    
    mixed_data = valid_data + invalid_data
    
    valid_objects, errors = validate_list(mixed_data, Fuu)
    
    assert len(valid_objects) == 2
    assert len(errors) == 2
    assert errors[0]["error"] == "Name must be a non-empty string"
    assert errors[1]["error"] == "Name must be a non-empty string"
    
    
def test_validate_full_name():
    valid_name = "Katarina Belka"
    first, last = validate_full_name(valid_name)
    assert first == "Katarina"
    assert last == "Belka"

    
def test_validate_full_name_invalid():
    invalid_name = "Katarina"
    with pytest.raises(ValueError, match='Incorrect full name format'):
        validate_full_name(invalid_name)


def test_validate_account_number():
    valid_account = "ID--ABC-123-456789"
    assert validate_account_number(valid_account) == valid_account

    invalid_length = "ID--ABC-12345"
    with pytest.raises(ValueError, match='Wrong length for account_number'):
        validate_account_number(invalid_length)

    invalid_start = "ABCD--ABC-123-4567"
    with pytest.raises(ValueError, match='account_number must start with "ID--"'):
        validate_account_number(invalid_start)

    invalid_account = "ID--AaB123-456789f"
    with pytest.raises(ValueError, match='Invalid ID format!'):
        validate_account_number(invalid_account)


def test_validate_field_value():
    valid_values = {"EUR", "USD", "UAH"}
    assert validate_field_value("EUR", valid_values, "currency") == "EUR"
    

def test_validate_field_value_invalid():
    valid_values = {"EUR", "USD", "UAH"}
    with pytest.raises(ValueError, match='Invalid value GBP for field currency!'):
        validate_field_value("GBP", valid_values, "currency")
        

def test_validate_amount():
    assert validate_amount(100.0) == 100.0

    with pytest.raises(ValueError, match='amount must be a number'):
        validate_amount("100")

    with pytest.raises(ValueError, match='amount cannot be negative'):
        validate_amount(-10)  
