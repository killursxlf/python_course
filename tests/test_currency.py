import pytest
from unittest.mock import MagicMock, patch
import requests
import currency

class FakeResponse:
    def __init__(self, json_data=None, status_code=200, raise_http=False):
        self._json = json_data or {}
        self.status_code = status_code
        self._raise_http = raise_http

    def raise_for_status(self):
        if self._raise_http:
            http_err = requests.HTTPError(f"HTTP {self.status_code} error")
            http_err.response = MagicMock(status_code=self.status_code)
            raise http_err

    def json(self):
        return self._json


def test_same_currency_returns_one():
    rate = currency.get_exchange_rate("USD", "USD")
    assert rate == 1.0


def test_successful_rate():
    fake_data = {"data": {"EUR": 0.85}}
    fake_resp = FakeResponse(json_data=fake_data)
    with patch("currency.requests.get", return_value=fake_resp), \
         patch("currency.logger") as mock_logger:
        rate = currency.get_exchange_rate("USD", "EUR")
        assert rate == 0.85
        mock_logger.info.assert_called_with("Exchange rate USD -> EUR = 0.85")


def test_no_rate_in_data_raises_runtime():
    fake_data = {"data": {"GBP": 0.75}}
    fake_resp = FakeResponse(json_data=fake_data)
    with patch("currency.requests.get", return_value=fake_resp), \
         patch("currency.logger") as mock_logger:
        with pytest.raises(RuntimeError) as exc:
            currency.get_exchange_rate("USD", "EUR")
        assert "No rate found for USD->EUR" in str(exc.value)
        mock_logger.error.assert_called()


def test_http_429_status_code():
    fake_resp = FakeResponse(status_code=429, raise_http=True)
    with patch("currency.requests.get", return_value=fake_resp), \
         patch("currency.logger") as mock_logger:
        with pytest.raises(RuntimeError) as exc:
            currency.get_exchange_rate("USD", "EUR")
        assert "API limit exceeded!" in str(exc.value)
        mock_logger.error.assert_called_with("API limit exceeded!")


def test_http_other_errors():
    fake_resp = FakeResponse(status_code=400, raise_http=True)
    with patch("currency.requests.get", return_value=fake_resp), \
         patch("currency.logger") as mock_logger:
        with pytest.raises(requests.HTTPError):
            currency.get_exchange_rate("USD", "EUR")
        mock_logger.error.assert_called()


def test_network_error_propagates():
    def fake_get(*args, **kwargs):
        raise Exception("Network failure")

    with patch("currency.requests.get", side_effect=fake_get), \
         patch("currency.logger") as mock_logger:
        with pytest.raises(Exception) as exc:
            currency.get_exchange_rate("USD", "EUR")
        assert "Network failure" in str(exc.value)
        mock_logger.error.assert_called_with("Currency API error: Network failure")
