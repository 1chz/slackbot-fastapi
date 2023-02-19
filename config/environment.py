import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(".env")
load_dotenv(dotenv_path=env_path)

SLACK_TOKEN = os.environ["SLACK_TOKEN"] or "Unable to read slack token"
SLACK_SIGNING_SECRET = (
    os.environ["SLACK_SIGNING_SECRET"] or "Unable to read slack signing secret"
)

CHATGPT_EMAIL = os.environ["CHATGPT_EMAIL"] or "Unable to read Chat-GPT email"
CHATGPT_PASSWORD = os.environ["CHATGPT_PASSWORD"] or "Unable to read Chat-GPT password"
