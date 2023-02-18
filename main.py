import logging
import os
import pathlib
import re
from typing import Tuple

from dacite import from_dict
from dotenv import load_dotenv
from fastapi import FastAPI
from revChatGPT.V1 import Chatbot
from slack_sdk import WebClient
from slackers.hooks import events, commands, actions
from slackers.server import router
from error.distribution import DistributionAbortError
from model.action import ActionEvent, ActionUsers, Container
from model.mention import MentionEvent, Mention
from model.slashcommand import SlashCommand

env_path = pathlib.Path(".env")
load_dotenv(dotenv_path=env_path)

# Create a app
app = FastAPI(debug=True)
app.include_router(router)
app.include_router(router, prefix="/slack")

# Create a SlackClient
slack = WebClient(os.environ["SLACK_TOKEN"])

# Set logging
logging.basicConfig(
    format="%(asctime)s --- %(levelname)s --- %(message)s",
    level=logging.INFO,
    datefmt="%Y-/%d-/%m'T'%I:%M:%S %p",
    filename="slackbot.log",
)

# Login OpenAPI
login = True
try:
    chatbot = Chatbot(
        config={
            "email": os.environ["CHATGPT_EMAIL"],
            "password": os.environ["CHATGPT_PASSWORD"],
        }
    )

except Exception:
    login = False


@events.on("app_mention")
async def handle_mention(bytestream: dict) -> None:
    event: MentionEvent = __unpickling_mentions(bytestream)

    question: str = __understanding_the_question(event.text)

    progress_emoji_id: str = __publish_progress_emoji(event)

    answer: str = __ask_chat_gpt(question)

    __remove_progress_emoji(event, progress_emoji_id)

    __publish_answer(event, answer)


def __unpickling_mentions(bytestream: dict) -> MentionEvent:
    return from_dict(data=bytestream, data_class=Mention).event


def __understanding_the_question(question: str) -> str:
    question = re.sub("\\s<@[^, ]*|(^)<@[^, ]*", "", question).strip()

    if question == "":
        return "질문을 제대로 이해하지 못했어요"

    else:
        return question


def __publish_progress_emoji(event: MentionEvent) -> str:
    slack_response = slack.chat_postMessage(
        mrkdwn=True, channel=event.channel, thread_ts=event.ts, text=":loading:"
    )

    return slack_response.data["ts"]


def __ask_chat_gpt(question: str) -> str:
    try:
        if not login:
            return "챗봇 서버에 로그인 할 수 없어요"

        answer = ""
        for data in chatbot.ask(question):
            answer = data["message"]

        return answer

    except Exception as e:
        logging.error(f"[{'app_mention':<30}] : {e}")
        return "요청이 너무 많아서 힘들어요"


def __remove_progress_emoji(event: MentionEvent, progress_emoji_id: str) -> None:
    slack.chat_delete(channel=event.channel, ts=progress_emoji_id)


def __publish_answer(event: MentionEvent, answer: str) -> None:
    slack.chat_postMessage(
        mrkdwn=True, channel=event.channel, thread_ts=event.ts, text=answer
    )


# TODO: 배포 커맨드('/release') 개발 완료 후 리팩토링 (이 TODO 주석 아래의 모든 코드)
@commands.on("release")
async def handle_command_release(bytestream: dict) -> None:
    # Unpickling
    command: SlashCommand = from_dict(data=bytestream, data_class=SlashCommand)

    # Check authorization
    if not __check_authorization(command.user_id):
        slack.chat_postMessage(
            mrkdwn=True,
            channel=command.channel_id,
            text=f"🚫 *<@{command.user_id}>님은 배포 권한이 없어요. 관리자에게 ID `{command.user_id}`를 전달해주세요.*",
        )
        return

    # Double check if you really want to release
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "*배포를 진행할까요?*"}},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "emoji": True, "text": "예"},
                    "style": "primary",
                    "value": "true",
                    "action_id": "release_approve",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "emoji": False, "text": "아니요"},
                    "style": "danger",
                    "value": "false",
                    "action_id": "release_reject",
                },
            ],
        },
    ]

    # Send button message (Approve or Reject)
    slack.chat_postMessage(channel=command.channel_id, blocks=blocks)


def __check_authorization(user_id: str) -> bool:
    with open("distributors.txt", "r") as distributors:
        if user_id not in [
            distributor.strip() for distributor in distributors.readlines()
        ]:
            return False

    return True


@actions.on("block_actions:release_reject")
async def handle_action_reject(bytestream: dict) -> None:
    try:
        user, container = __preprocessing_release(
            action_event=from_dict(data=bytestream, data_class=ActionEvent)
        )

        slack.chat_postMessage(
            mrkdwn=True,
            channel=container.channel_id,
            text=f"🚀 *<@{user.id}>님이 배포를 취소했어요*",
        )

    except DistributionAbortError as e:
        logging.error(f"[{'block_actions:release_reject':<30}] : {e}")
        return


def __preprocessing_release(action_event: ActionEvent) -> Tuple[ActionUsers, Container]:
    user = action_event.user
    container = action_event.container

    if not __check_authorization(user.id):
        slack.chat_postMessage(
            mrkdwn=True,
            channel=container.channel_id,
            text=f"🚫 *<@{user.id}>님은 배포 권한이 없어요. 관리자에게 ID `{user.id}`를 전달해 주세요*",
        )
        raise DistributionAbortError("User is not authorized to release.")

    slack.chat_delete(channel=container.channel_id, ts=container.message_ts)

    return user, container


@actions.on("block_actions:release_approve")
async def handle_action_approve(bytestream: dict) -> None:
    try:
        user, container = __preprocessing_release(
            action_event=from_dict(data=bytestream, data_class=ActionEvent)
        )

        message = f"🚀 *<@{user.id}>님이 배포를 시작했어요*"
        logging.info(f"[{'release started':<30}] : {message}")
        thread_id = slack.chat_postMessage(
            mrkdwn=True, channel=container.channel_id, text=message
        )

        # TODO: 배포 진행 및 상황을 스레드(thread_id)에 코멘팅

    except DistributionAbortError as e:
        logging.error(f"[{'block_actions:release_approve':<30}] : {e}")
        return
