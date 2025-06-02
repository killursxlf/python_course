from unittest.mock import patch
from transfer import do_transfer
from dataclasses import dataclass
from queries import UPDATE_ACCOUNT_AMOUNT_BY_ID

@dataclass
class Account:
    id: int = None
    type: str = None
    account_number: str = None
    currency: str = None
    amount: float = 0.0


def test_do_transfer_not_enough(fake_cursor):
    sender = Account(id=1, account_number='ACC1', amount=50.0, currency='USD', type='checking')
    receiver = Account(id=2, account_number='ACC2', amount=20.0, currency='USD', type='checking')

    expected = {'success': False, 'message': 'Not enough funds', 'status_code': 400}
    with patch("transfer.api_response", return_value=expected):
        resp = do_transfer(fake_cursor, sender, receiver, 100.0)

    assert resp == expected
    fake_cursor.execute.assert_not_called()


def test_do_transfer_currency_api_error(fake_cursor):
    sender = Account(id=1, account_number='ACC1', amount=200.0, currency='USD', type='checking')
    receiver = Account(id=2, account_number='ACC2', amount=100.0, currency='EUR', type='checking')

    expected = {
        'success': False,
        'message': 'Currency API error: API down',
        'status_code': 502
    }

    with patch("transfer.get_exchange_rate", side_effect=Exception("API down")), \
         patch("transfer.api_response", return_value=expected):
        resp = do_transfer(fake_cursor, sender, receiver, 50.0)

    assert resp == expected
    fake_cursor.execute.assert_not_called()


def test_do_transfer_same_currency_success(fake_cursor):
    sender = Account(id=1, account_number='ACC1', amount=300.0, currency='USD', type='checking')
    receiver = Account(id=2, account_number='ACC2', amount=150.0, currency='USD', type='checking')

    expected = {
        'success': True,
        'message': ["Transferred 100.0 USD from ACC1 to ACC2"],
        'status_code': 200
    }

    def fake_api(success, message, status_code, log_type):
        return expected

    with patch("transfer.api_response", side_effect=fake_api):
        resp = do_transfer(fake_cursor, sender, receiver, 100.0)

    fake_cursor.execute.assert_any_call(
        UPDATE_ACCOUNT_AMOUNT_BY_ID, (200.0, sender.id)
    )
    fake_cursor.execute.assert_any_call(
        UPDATE_ACCOUNT_AMOUNT_BY_ID, (250.0, receiver.id)
    )

    assert resp == expected


def test_do_transfer_different_currency_success(fake_cursor):
    sender = Account(id=1, account_number='ACC1', amount=500.0, currency='USD', type='checking')
    receiver = Account(id=2, account_number='ACC2', amount=200.0, currency='EUR', type='checking')

    expected = {
        'success': True,
        'message': ["Transferred 200.0 USD from ACC1 to ACC2 (converted to 100.0 EUR)"],
        'status_code': 200
    }

    def fake_api(success, message, status_code, log_type):
        return expected

    with patch("transfer.get_exchange_rate", return_value=0.5), \
         patch("transfer.api_response", side_effect=fake_api):
        resp = do_transfer(fake_cursor, sender, receiver, 200.0)

    fake_cursor.execute.assert_any_call(
        UPDATE_ACCOUNT_AMOUNT_BY_ID, (300.0, sender.id)
    )
    fake_cursor.execute.assert_any_call(
        UPDATE_ACCOUNT_AMOUNT_BY_ID, (300.0, receiver.id)
    )

    assert resp == expected
