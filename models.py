from dataclasses import dataclass
from validator import (
    validate_full_name,
    validate_account_number,
    validate_field_value,
    validate_amount
)
from config import (
    ALLOWED_ACCOUNT_TYPES,
    ALLOWED_ACCOUNT_STATUS,
    ALLOWED_CURRENCIES
)


@dataclass
class Bank:
    id: int = None
    name: str = None

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Bank name must be a string and cannot be empty")
        self.name = self.name.strip()

    @classmethod
    def built_from_dict(cls, row: dict):
        return cls(
            id=int(row.get("id", 0)) if row.get("id") else None,
            name=row["name"]
        )

    @classmethod
    def from_name(cls, name: str):
        return cls(name=name)


@dataclass
class User:
    id: int = None
    name: str = None
    surname: str = None
    birth_day: str = None
    accounts: str = ""

    def __post_init__(self):
        if not self.name or not self.surname:
            raise ValueError("Name and Surname cannot be empty")
        if self.accounts is None:
            self.accounts = ""

    @classmethod
    def built_from_dict(cls, row: dict):
        if "user_full_name" in row:
            name, surname = validate_full_name(row["user_full_name"])
        else:
            name = row.get("name")
            surname = row.get("surname")
        return cls(
            id=int(row.get("id", 0)) if row.get("id") else None,
            name=name,
            surname=surname,
            birth_day=row.get("birth_day"),
            accounts=row.get("accounts", "")
        )

    @classmethod
    def from_full_name(cls, full_name: str, birth_day=None, accounts=""):
        name, surname = validate_full_name(full_name)
        return cls(name=name, surname=surname, birth_day=birth_day, accounts=accounts)


@dataclass
class Account:
    id: int = None
    user_id: int = None
    type: str = None
    account_number: str = None
    bank_id: int = None
    currency: str = None
    amount: float = 0.0
    status: str = None

    def __post_init__(self):
        self.type = validate_field_value(self.type, ALLOWED_ACCOUNT_TYPES, "type")
        self.account_number = validate_account_number(self.account_number)
        self.status = validate_field_value(self.status, ALLOWED_ACCOUNT_STATUS, "status")
        self.currency = validate_field_value(self.currency, ALLOWED_CURRENCIES, "currency")
        self.amount = validate_amount(self.amount)

    @classmethod
    def built_from_dict(cls, row: dict):
        return cls(
            id=int(row.get("id")) if row.get("id") else None,
            user_id=int(row["user_id"]),
            type=row["type"],
            account_number=row["account_number"],
            bank_id=int(row["bank_id"]),
            currency=row["currency"],
            amount=float(row["amount"]),
            status=row["status"]
        )


@dataclass
class Transaction:
    id: int = None
    bank_sender_name: str = None
    account_sender_id: int = None
    bank_receiver_name: str = None
    account_receiver_id: int = None
    sent_currency: str = None
    sent_amount: float = 0.0
    datetime: str = None

    def __post_init__(self):
        if not self.bank_sender_name or not self.bank_receiver_name:
            raise ValueError("bank_sender_name and bank_receiver_name cannot be empty")
        if not isinstance(self.account_sender_id, int) or not isinstance(self.account_receiver_id, int):
            raise ValueError("account_sender_id and account_receiver_id must be int")
        if not self.sent_currency or not isinstance(self.sent_currency, str):
            raise ValueError("sent_currency cannot be empty")
        self.sent_amount = validate_amount(self.sent_amount)

    @classmethod
    def built_from_dict(cls, row: dict):
        return cls(
            id=int(row.get("id", 0)) if row.get("id") else None,
            bank_sender_name=row["bank_sender_name"],
            account_sender_id=int(row["account_sender_id"]),
            bank_receiver_name=row["bank_receiver_name"],
            account_receiver_id=int(row["account_receiver_id"]),
            sent_currency=row["sent_currency"],
            sent_amount=float(row["sent_amount"]),
            datetime=row.get("datetime")
        )
