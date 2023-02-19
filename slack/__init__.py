from config.environment import SLACK_TOKEN
from slack_sdk import WebClient

slack = WebClient(SLACK_TOKEN)
