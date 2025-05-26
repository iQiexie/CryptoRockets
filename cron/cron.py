import os
import urllib.request
from datetime import datetime

from dotenv import load_dotenv

load_dotenv("/usr/app/.env")


url = "http://127.0.0.1:8000" + os.getenv("URL")
headers = {"token": os.getenv("AUTH_TOKEN_TASK").strip()}
req = urllib.request.Request(url, headers=headers)

print(f"Sending request to {url=}, {headers=}")
with urllib.request.urlopen(req) as response:
    response_text = response.read().decode("utf-8")
    response_code = response.getcode()

print(f"{datetime.utcnow()} - {response_code}: {response_text}")  # noqa
