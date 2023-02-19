import logging

from fastapi import FastAPI

# noinspection PyUnresolvedReferences
from slack.action import handle_action_approve, handle_action_reject

# noinspection PyUnresolvedReferences
from slack.mention import handle_mention

# noinspection PyUnresolvedReferences
from slack.slashcmd import handle_command_release
from slackers.server import router

# Create a app
app = FastAPI(debug=True)
app.include_router(router, prefix="/slack")

# Set logging
logging.basicConfig(
    format="%(asctime)s --- %(levelname)s --- %(message)s",
    level=logging.INFO,
    datefmt="%Y-/%d-/%m'T'%I:%M:%S %p",
    filename="slackbot.log",
)
