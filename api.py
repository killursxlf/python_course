from db import with_db_connection
from models import User, Bank, Account
from logging_config import get_logger
from helpers import api_response
from transfer import do_transfer
from queries import insert_rows, update_row, delete_row
from validator import validate_list
from queries import INSERT_TRANSACTION, SELECT_ACCOUNT_BY_ID, SELECT_BANK_NAME_BY_ID

logger = get_logger(__name__)


def unpack_rows(*args):
    if len(args) == 1 and isinstance(args[0], list):
        return args[0]
    return list(args)


def add_objects(
    cur,
    raw_items: tuple,
    table: str,
    fields: list[str],
    cls: type,
):
    """
    Generic bulk-insert into a table of dataclass instances.

    Args:
        conn: Active SQLite connection.
        raw_items: Tuple or list of items to insert (dataclass instances or dicts).
        table: Name of the target database table.
        fields: List of column names to populate.
        cls: Dataclass type used for validation.

    Returns:
        dict: API response with keys:
            - success (bool)
            - message (str)
            - status_code (int)
    """
    items = unpack_rows(*raw_items)

    if any(isinstance(i, dict) for i in items):
        raw_dicts = [i if isinstance(i, dict) else i.__dict__ for i in items]
        valid, errors = validate_list(raw_dicts, cls)
        items = valid
        if errors:
            logger.warning(
                "%s %s rows failed validation, skipped",
                len(errors),
                cls.__name__
            )

    try:
        count = insert_rows(cur, table, fields, items)
        return api_response(True, f"{cls.__name__}s added: {count}")
    except Exception as e:
        return api_response(False, f"Error adding {cls.__name__}: {e}", 500, "error")


def update_object(cur, obj, table: str, fields: list[str], pk_field: str):
    """
    Generic update function for a single dataclass row.
    Args:
        conn: active db connection
        obj: dataclass instance
        table: table name (str)
        fields: list of fields to update (list[str])
        pk_field: primary key field (e.g. 'id')
        logger_name: name for logger
    Returns:
        dict with api_response
    """
    try:
        if getattr(obj, pk_field, None) is None:
            return api_response(
                False,
                f"{table[:-1].capitalize()} {pk_field} is required for update",
                400,
                "warning",
            )
        rowcount = update_row(cur, table, fields, pk_field, obj)
        if rowcount == 0:
            return api_response(
                False, f"{table[:-1].capitalize()} not found", 404, "warning"
            )
        logger.info(
            "%s with %s=%s updated",
            table[:-1].capitalize(),
            pk_field,
            getattr(obj, pk_field)
        )
        return api_response(
            True,
            f"{table[:-1].capitalize()} with {pk_field}={getattr(obj, pk_field)} updated"
        )
    except Exception as e:
        logger.error("Error updating %s: %s", table[:-1].capitalize(), e)
        return api_response(
            False, f"Error updating {table[:-1].capitalize()}: {e}", 500, "error"
        )


def delete_object(cur, table: str, pk_field: str, pk_value: int):
    """
    Generic delete function for a single row.
    Args:
        conn: db connection
        table: table name
        pk_field: primary key field (e.g. "id")
        pk_value: value of the primary key
        logger_name: name for logger
    Returns:
        dict with api_response
    """
    try:
        rowcount = delete_row(cur, table, pk_field, pk_value)
        if rowcount == 0:
            logger.warning(
                "%s with %s=%s not found for deletion",
                table[:-1].capitalize(),
                pk_field,
                pk_value
            )
            return api_response(
                False, f"{table[:-1].capitalize()} not found", 404, "warning"
            )
        logger.info("%s with %s=%s deleted", table[:-1].capitalize(), pk_field, pk_value)
        return api_response(
            True, f"{table[:-1].capitalize()} with {pk_field}={pk_value} deleted"
        )
    except Exception as e:
        logger.error("Error deleting %s: %s", table[:-1].capitalize(), e)
        return api_response(
            False, f"Error deleting {table[:-1].capitalize()}: {e}", 500, "error"
        )


@with_db_connection
def add_banks(cur, *banks):
    return add_objects(cur, banks, table="Bank", fields=["name"], cls=Bank)


@with_db_connection
def add_users(cur, *users):
    return add_objects(
        cur,
        users,
        table="User",
        fields=["name", "surname", "birth_day", "accounts"],
        cls=User,
    )


@with_db_connection
def add_accounts(cur, *accounts):
    return add_objects(
        cur,
        accounts,
        table="Account",
        fields=[
            "user_id",
            "type",
            "account_number",
            "bank_id",
            "currency",
            "amount",
            "status",
        ],
        cls=Account,
    )


@with_db_connection
def update_user(cur, user: User):
    return update_object(
        cur,
        user,
        table="User",
        fields=["name", "surname", "birth_day", "accounts"],
        pk_field="id",
    )


@with_db_connection
def update_bank(cur, bank: Bank):
    return update_object(cur, bank, table="Bank", fields=["name"], pk_field="id")


@with_db_connection
def update_account(cur, account: Account):
    return update_object(
        cur,
        account,
        table="Account",
        fields=[
            "user_id",
            "type",
            "account_number",
            "bank_id",
            "currency",
            "amount",
            "status",
        ],
        pk_field="id",
    )


@with_db_connection
def delete_user(cur, user_id: int):
    return delete_object(cur, table="User", pk_field="id", pk_value=user_id)


@with_db_connection
def delete_bank(cur, bank_id: int):
    return delete_object(cur, table="Bank", pk_field="id", pk_value=bank_id)


@with_db_connection
def delete_account(cur, account_id: int):
    return delete_object(cur, table="Account", pk_field="id", pk_value=account_id)


@with_db_connection
def transfer_money(
    cur, sender_account_id: int, receiver_account_id: int, amount: float
):

    sender, error = get_client_by_id(cur, sender_account_id)
    if error:
        return error

    receiver, error = get_client_by_id(cur, receiver_account_id)
    if error:
        return error

    transfer_result = do_transfer(cur, sender, receiver, amount)
    if not transfer_result["success"]:
        return transfer_result

    cur.execute(
        INSERT_TRANSACTION,
        (
            _get_bank_name(cur, sender.bank_id),
            sender.id,
            _get_bank_name(cur, receiver.bank_id),
            receiver.id,
            sender.currency,
            amount,
        ),
    )
    return transfer_result


def get_client_by_id(cur, client_id):
    cur.execute(SELECT_ACCOUNT_BY_ID, (client_id,))
    client_row = cur.fetchone()
    if not client_row:
        return None, api_response(False, "Client account not found", 404, "warning")
    return Account(*client_row), None


def _get_bank_name(cur, bank_id):
    cur.execute(SELECT_BANK_NAME_BY_ID, (bank_id,))
    row = cur.fetchone()
    return row[0] if row else "Unknown"
