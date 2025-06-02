from unittest.mock import patch
from analytics import (
    assign_random_discounts,
    get_users_with_debt,
    bank_with_biggest_capital,
    bank_with_oldest_client,
    bank_with_most_active_users,
    delete_incomplete_users_and_accounts,
    user_transactions_last_3_months
)

# assign_random_discounts

def test_assign_random_discounts_ok(fake_cursor):
    fake_cursor.fetchall.return_value = [(1,), (2,), (3,)]
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "message": "Discounts assigned", "status_code": 200, "discounts": {1: 25}}
        mock_api_response.return_value = expected_result
        result = assign_random_discounts.__wrapped__(fake_cursor)
        assert result == expected_result


def test_assign_random_discounts_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = assign_random_discounts.__wrapped__(fake_cursor)
        assert result == expected_result

# get_users_with_debt

def test_get_users_with_debt_ok(fake_cursor):
    fake_cursor.fetchall.return_value = [("John", "Doe"), ("Jane", "Doe")]
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "message": "Users with debts", "status_code": 200, "users": ["John Doe", "Jane Doe"]}
        mock_api_response.return_value = expected_result
        result = get_users_with_debt.__wrapped__(fake_cursor)
        assert result == expected_result


def test_get_users_with_debt_no_data(fake_cursor):
    fake_cursor.fetchall.return_value = []
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "message": "Users with debts", "status_code": 200, "users": []}
        mock_api_response.return_value = expected_result
        result = get_users_with_debt.__wrapped__(fake_cursor)
        assert result == expected_result


def test_get_users_with_debt_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = get_users_with_debt.__wrapped__(fake_cursor)
        assert result == expected_result

# bank_with_biggest_capital

def test_bank_with_biggest_capital_ok(fake_cursor):
    fake_cursor.fetchone.return_value = (1, "Big Bank", 5000000)
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "bank_id": 1, "name": "Big Bank", "capital": 5000000, "status_code": 200}
        mock_api_response.return_value = expected_result
        result = bank_with_biggest_capital.__wrapped__(fake_cursor)
        assert result == expected_result


def test_bank_with_biggest_capital_no_data(fake_cursor):
    fake_cursor.fetchone.return_value = None
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "No data", "status_code": 404}
        mock_api_response.return_value = expected_result
        result = bank_with_biggest_capital.__wrapped__(fake_cursor)
        assert result == expected_result


def test_bank_with_biggest_capital_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = bank_with_biggest_capital.__wrapped__(fake_cursor)
        assert result == expected_result

# bank_with_oldest_client

def test_bank_with_oldest_client_ok(fake_cursor):
    fake_cursor.fetchone.return_value = (2, "Old Bank", 101, "Alice", "Smith", "1930-01-01")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {
            "success": True,
            "bank_id": 2,
            "bank_name": "Old Bank",
            "user_id": 101,
            "client": "Alice Smith",
            "birth_day": "1930-01-01",
            "status_code": 200
        }
        mock_api_response.return_value = expected_result
        result = bank_with_oldest_client.__wrapped__(fake_cursor)
        assert result == expected_result


def test_bank_with_oldest_client_no_data(fake_cursor):
    fake_cursor.fetchone.return_value = None
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "No data", "status_code": 404}
        mock_api_response.return_value = expected_result
        result = bank_with_oldest_client.__wrapped__(fake_cursor)
        assert result == expected_result


def test_bank_with_oldest_client_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = bank_with_oldest_client.__wrapped__(fake_cursor)
        assert result == expected_result

# bank_with_most_active_users

def test_bank_with_most_active_users_ok(fake_cursor):
    fake_cursor.fetchone.return_value = ("Active Bank", 150)
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "bank_name": "Active Bank", "user_count": 150, "status_code": 200}
        mock_api_response.return_value = expected_result
        result = bank_with_most_active_users.__wrapped__(fake_cursor)
        assert result == expected_result


def test_bank_with_most_active_users_no_data(fake_cursor):
    fake_cursor.fetchone.return_value = None
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "No data", "status_code": 404}
        mock_api_response.return_value = expected_result
        result = bank_with_most_active_users.__wrapped__(fake_cursor)
        assert result == expected_result


def test_bank_with_most_active_users_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = bank_with_most_active_users.__wrapped__(fake_cursor)
        assert result == expected_result

# delete_incomplete_users_and_accounts

def test_delete_incomplete_users_and_accounts_ok(fake_cursor):
    fake_cursor.rowcount = 3
    def side_effect(*args, **kwargs):
        return None
    fake_cursor.execute.side_effect = side_effect
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "accounts_deleted": 3, "users_deleted": 3, "status_code": 200}
        mock_api_response.return_value = expected_result
        result = delete_incomplete_users_and_accounts.__wrapped__(fake_cursor)
        assert result == expected_result


def test_delete_incomplete_users_and_accounts_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = delete_incomplete_users_and_accounts.__wrapped__(fake_cursor)
        assert result == expected_result

# user_transactions_last_3_months

def test_user_transactions_last_3_months_ok(fake_cursor):
    fake_cursor.fetchall.side_effect = [[(10,), (20,)], [("txn1", 100), ("txn2", 200)]]
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": True, "transactions": [("txn1", 100), ("txn2", 200)], "status_code": 200}
        mock_api_response.return_value = expected_result
        result = user_transactions_last_3_months.__wrapped__(fake_cursor, 123)
        assert result == expected_result


def test_user_transactions_last_3_months_no_data(fake_cursor):
    fake_cursor.fetchall.return_value = []
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "status_code": 404}
        mock_api_response.return_value = expected_result
        result = user_transactions_last_3_months.__wrapped__(fake_cursor, 123)
        assert result == expected_result


def test_user_transactions_last_3_months_exception(fake_cursor):
    fake_cursor.execute.side_effect = Exception("DB Error")
    with patch("analytics.api_response") as mock_api_response:
        expected_result = {"success": False, "message": "DB Error", "status_code": 500}
        mock_api_response.return_value = expected_result
        result = user_transactions_last_3_months.__wrapped__(fake_cursor, 123)
        assert result == expected_result
