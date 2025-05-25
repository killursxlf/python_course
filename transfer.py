from models import Account
from currency import get_exchange_rate
from helpers import api_response

def do_transfer(cur, sender: Account, receiver: Account, amount: float):
    if sender.amount < amount:
        return api_response(False, "Not enough funds", 400, "warning")

    if sender.currency != receiver.currency:
        try:
            rate = get_exchange_rate(sender.currency, receiver.currency)
        except Exception as e:
            return api_response(False, f"Currency API error: {e}", 502, "error")
        receiver_amount = round(amount * rate, 2)
    else:
        receiver_amount = amount

    new_sender_balance = sender.amount - amount
    new_receiver_balance = receiver.amount + receiver_amount

    cur.execute("UPDATE Account SET amount=? WHERE id=?", (new_sender_balance, sender.id))
    cur.execute("UPDATE Account SET amount=? WHERE id=?", (new_receiver_balance, receiver.id))

    return api_response(
        True,
        f"Transferred {amount} {sender.currency} from {sender.account_number} to {receiver.account_number} ({receiver_amount} {receiver.currency})",
        200,
        "info"
    )
