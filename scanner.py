import sqlite3
import time
from typing import TypedDict

import requests
import structlog

from app.config.config import get_config
from app.init.logs import setup_logs


class WebhookData(TypedDict):
    hash: str
    amount: float
    payload: str


config = get_config()
setup_logs(config=config.logs)
logger = structlog.stdlib.get_logger()

ADDRESS = config.scanner.SCANNER_WALLET
WEBHOOK_URL = config.scanner.SCANNER_WEBHOOK_URL

conn = sqlite3.connect("./db-data/transactions.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS transactions (hash TEXT PRIMARY KEY)")
conn.commit()

logger.info("Started scanning for transactions...")


def send_webhook(data: WebhookData) -> None:
    max_retries = 60
    retry_delay = 1  # seconds

    for attempt in range(1, max_retries + 1):
        logger.info(f"Sending (Attempt {attempt}/{max_retries}) to {WEBHOOK_URL}", data=data)
        try:
            resp = requests.post(url=WEBHOOK_URL, json=data, timeout=10)
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}", hash=data["hash"])
            time.sleep(retry_delay)
            continue

        logger.info(f"Status {resp.status_code=}, Response: {resp.text=}", hash=data["hash"])

        if resp.status_code != 502:  # noqa: PLR2004
            break  # Success or other error, stop retrying

        time.sleep(retry_delay)


def fetch_transactions() -> list:
    try:
        response = requests.get(
            url="https://toncenter.com/api/v2/getTransactions",
            headers={"accept": "application/json"},
            params={"address": ADDRESS, "limit": "10", "lt": "0", "to_lt": "0", "archival": "true"},
            timeout=10,
        )
        if response.status_code != 200:  # noqa: PLR2004
            logger.error(f"Error fetching transactions: {response.status_code=} {response.text=}")
            return []
        return response.json().get("result", [])
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return []


def transaction_exists(hash_: str) -> bool:
    cursor.execute("SELECT 1 FROM transactions WHERE hash = ?", (hash_,))
    return cursor.fetchone() is not None


def save_transaction_hash(hash_: str) -> None:
    cursor.execute("INSERT INTO transactions (hash) VALUES (?)", (hash_,))
    conn.commit()


def process_transaction(tx: dict) -> None:
    hash_ = tx["transaction_id"]["hash"]
    if transaction_exists(hash_):
        return

    amount = round(int(tx["in_msg"]["value"]) / 1_000_000_000, 2)
    payload = tx["in_msg"]["message"]

    logger.info(f"Hash: {hash_}, Amount: {amount}, Payload: {payload}", hash=hash_)

    save_transaction_hash(hash_)
    send_webhook(data=WebhookData(hash=hash_, amount=amount, payload=payload))


def main() -> None:
    while True:
        time.sleep(2)
        for tx in fetch_transactions():
            try:
                process_transaction(tx)
            except Exception as e:
                logger.error(event=f"Malformed transaction data: {tx=}, {e=}")


if __name__ == "__main__":
    main()
