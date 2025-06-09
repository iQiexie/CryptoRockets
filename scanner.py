import sqlite3
import time
from datetime import datetime

import requests
import structlog

from app.config.config import get_config
from app.init.logs import setup_logs

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

while True:
    response = requests.get(
        url="https://toncenter.com/api/v2/getTransactions",
        headers={"accept": "application/json"},
        params={
            "address": ADDRESS,
            "limit": "10",
            "lt": "0",
            "to_lt": "0",
            "archival": "true",
        },
    )

    if response.status_code != 200:
        logger.error(f"Error fetching transactions: {response.status_code=} {response.text=}")
        time.sleep(5)
        continue

    transactions = response.json().get("result", [])

    for tx in transactions:
        try:
            hash_ = tx["transaction_id"]["hash"]
            amount = round(int(tx["in_msg"]["value"]) / 1_000_000_000, 2)
            payload = tx["in_msg"]["message"]

            # Check if hash already exists in DB
            cursor.execute("SELECT 1 FROM transactions WHERE hash = ?", (hash_,))
            if cursor.fetchone():
                continue  # Skip if already exists

            # Insert new hash into DB
            cursor.execute("INSERT INTO transactions (hash) VALUES (?)", (hash_,))
            conn.commit()

            logger.info(f"[{datetime.now()}] [{hash_}] Hash: {hash_}, Amount: {amount}, Payload: {payload}")

            new_tx = {"hash": hash_, "amount": amount, "payload": payload}

            logger.info(f"[{datetime.now()}] [{hash_}] Sending {new_tx} to {WEBHOOK_URL}")
            webhook_resp = requests.post(url=WEBHOOK_URL, json=new_tx)
            logger.info(f"[{datetime.now()}] [{hash_}] Status {webhook_resp.status_code}, Response: {webhook_resp.text}")

        except (TypeError, KeyError):
            logger.error("Malformed transaction data:", tx)

    time.sleep(2)  # Add a small delay to avoid hammering the API
