import pytest
from unittest.mock import patch
from models import Bank, User, Account, Transaction

# --- Constants and Mocks ---

ALLOWED_ACCOUNT_TYPES = ["savings", "checking"]
ALLOWED_ACCOUNT_STATUS = ["active", "inactive"]
ALLOWED_CURRENCIES = ["USD", "EUR"]

def mock_validate_full_name(full):
    return ["Lisa", "Konig"]

def mock_validate_account_number(acc_id):
    return acc_id

def mock_validate_field_value(value, allowed, field):
    if value not in allowed:
        raise ValueError(f"{field} not allowed")
    return value

def mock_validate_amount(x):
    if x < 0:
        raise ValueError("Negative amount")
    return x

# --- Bank tests ---

@pytest.mark.parametrize(
    "name, expected_name, should_raise",
    [
        ("  Sparkasse ", "Sparkasse", False), 
        ("", None, True),                     
    ]
)
def test_bank_post_init(name, expected_name, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            Bank(name=name)
    else:
        bank = Bank(name=name)
        assert bank.name == expected_name

def test_bank_built_from_dict():
    row = {"id": "1", "name": "Deutsche Bank"}
    bank = Bank.built_from_dict(row)
    assert bank.id == 1
    assert bank.name == "Deutsche Bank"

# --- User tests ---

@pytest.mark.parametrize(
    "name, surname, accounts, should_raise",
    [
        ("Anna", "Muller", None, False),  
        ("", "Smith", None, True),        
    ]
)
def test_user_post_init(name, surname, accounts, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            User(name=name, surname=surname, accounts=accounts)
    else:
        user = User(name=name, surname=surname, accounts=accounts)
        assert user.name == name
        assert user.surname == surname
        assert user.accounts == ""


@patch("validator.validate_full_name", side_effect=mock_validate_full_name)
def test_user_built_from_dict_with_full_name(mock_val):
    row = {
        "id": "2",
        "user_full_name": "Lisa Konig",
        "birth_day": "1991-01-01",
        "accounts": "A1,A2"
    }
    user = User.built_from_dict(row)
    assert user.name == "Lisa"
    assert user.surname == "Konig"


@patch("validator.validate_full_name", side_effect=mock_validate_full_name)
def test_user_built_from_dict_without_full_name(mock_val):
    row = {
        "id": "3",
        "name": "Markus",
        "surname": "Weber",
        "birth_day": "1990-05-05",
        "accounts": "B1"
    }
    user = User.built_from_dict(row)
    assert user.name == "Markus"
    assert user.surname == "Weber"

# --- Account tests ---

@patch("models.validate_amount", side_effect=mock_validate_amount)
@patch("models.validate_account_number", side_effect=mock_validate_account_number)
@patch("models.validate_field_value", side_effect=mock_validate_field_value)
def test_account_built_from_dict(mock_val_field, mock_val_accnum, mock_val_amount):
    with patch("models.ALLOWED_ACCOUNT_TYPES", new=ALLOWED_ACCOUNT_TYPES), \
         patch("models.ALLOWED_ACCOUNT_STATUS", new=ALLOWED_ACCOUNT_STATUS), \
         patch("models.ALLOWED_CURRENCIES", new=ALLOWED_CURRENCIES):

        row = {
            "id": "4",
            "user_id": "11",
            "type": "checking",
            "account_number": "456-789",
            "bank_id": "2",
            "currency": "EUR",
            "amount": "1234.5",
            "status": "inactive"
        }
        acc = Account.built_from_dict(row)
        assert acc.id == 4
        assert acc.user_id == 11
        assert acc.account_number == "456-789"
        assert acc.amount == 1234.5

# --- Transaction tests ---

@patch("validator.validate_amount", side_effect=mock_validate_amount)
def test_transaction_post_init_valid(mock_val):
    txn = Transaction(
        bank_sender_name="Bank A",
        account_sender_id=1,
        bank_receiver_name="Bank B",
        account_receiver_id=2,
        sent_currency="USD",
        sent_amount=99.99,
        datetime="2025-01-01"
    )
    assert txn.sent_amount == 99.99
    assert txn.bank_sender_name == "Bank A"

@patch("validator.validate_amount", lambda x: x)
@pytest.mark.parametrize(
    "bank_sender, account_sender, bank_receiver, account_receiver, currency, should_raise",
    [
        ("BankA", 1, "BankB", 2, "USD", False),    
        ("", 1, "BankB", 2, "USD", True),         
        ("BankA", 1, "", 2, "USD", True),         
        ("BankA", "abc", "BankB", 2, "USD", True), 
        ("BankA", 1, "BankB", "xyz", "USD", True),  
        ("BankA", 1, "BankB", 2, "", True),         
        ("BankA", 1, "BankB", 2, 123, True),        
    ]
)
def test_transaction_post_init_all_cases(bank_sender, account_sender, bank_receiver, account_receiver, currency, should_raise):
    if should_raise:
        with pytest.raises(ValueError):
            Transaction(
                bank_sender_name=bank_sender,
                account_sender_id=account_sender,
                bank_receiver_name=bank_receiver,
                account_receiver_id=account_receiver,
                sent_currency=currency,
                sent_amount=100.0,
                datetime="2025-01-01"
            )
    else:
        txn = Transaction(
            bank_sender_name=bank_sender,
            account_sender_id=account_sender,
            bank_receiver_name=bank_receiver,
            account_receiver_id=account_receiver,
            sent_currency=currency,
            sent_amount=100.0,
            datetime="2025-01-01"
        )
        assert txn.sent_amount == 100.0

@patch("validator.validate_amount", side_effect=mock_validate_amount)
def test_transaction_built_from_dict(mock_val):
    row = {
        "id": "8",
        "bank_sender_name": "SenderBank",
        "account_sender_id": "4",
        "bank_receiver_name": "ReceiverBank",
        "account_receiver_id": "5",
        "sent_currency": "EUR",
        "sent_amount": "200.0",
        "datetime": "2025-06-01T10:00:00"
    }
    txn = Transaction.built_from_dict(row)
    assert txn.id == 8
    assert txn.account_sender_id == 4
    assert txn.account_receiver_id == 5
    assert txn.sent_amount == 200.0
