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

def test_bank_post_init_valid():
    bank = Bank(name="  Sparkasse ")
    assert bank.name == "Sparkasse"


def test_bank_post_init_invalid():
    with pytest.raises(ValueError):
        Bank(name="")


def test_bank_built_from_dict():
    row = {"id": "1", "name": "Deutsche Bank"}
    bank = Bank.built_from_dict(row)
    assert bank.id == 1
    assert bank.name == "Deutsche Bank"

# --- User tests ---

def test_user_post_init_valid():
    user = User(name="Anna", surname="Muller", accounts=None)
    assert user.name == "Anna"
    assert user.surname == "Muller"
    assert user.accounts == ""


def test_user_post_init_invalid():
    with pytest.raises(ValueError):
        User(name="", surname="Smith", accounts=None)


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
def test_transaction_post_init_all_valid():
    txn = Transaction(
        bank_sender_name="BankA",
        account_sender_id=1,
        bank_receiver_name="BankB",
        account_receiver_id=2,
        sent_currency="USD",
        sent_amount=100.0,
        datetime="2025-01-01"
    )
    assert txn.sent_amount == 100.0


@patch("validator.validate_amount", lambda x: x)
def test_transaction_post_init_missing_sender_name():
    with pytest.raises(ValueError):
        Transaction("",
                    1, "BankB", 2, "USD", 100.0, "2025-01-01")


@patch("validator.validate_amount", lambda x: x)
def test_transaction_post_init_missing_receiver_name():
    with pytest.raises(ValueError):
        Transaction("BankA",
                    1, "", 2, "USD", 100.0, "2025-01-01")


@patch("validator.validate_amount", lambda x: x)
def test_transaction_post_init_sender_id_not_int():
    with pytest.raises(ValueError):
        Transaction("BankA",
                    "abc", "BankB", 2, "USD", 100.0, "2025-01-01")


@patch("validator.validate_amount", lambda x: x)
def test_transaction_post_init_receiver_id_not_int():
    with pytest.raises(ValueError):
        Transaction("BankA",
                    1, "BankB", "xyz", "USD", 100.0, "2025-01-01")


@patch("validator.validate_amount", lambda x: x)
def test_transaction_post_init_currency_empty():
    with pytest.raises(ValueError):
        Transaction("BankA",
                    1, "BankB", 2, "", 100.0, "2025-01-01")


@patch("validator.validate_amount", lambda x: x)
def test_transaction_post_init_currency_not_str():
    with pytest.raises(ValueError):
        Transaction("BankA",
                    1, "BankB", 2, 123, 100.0, "2025-01-01")


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
