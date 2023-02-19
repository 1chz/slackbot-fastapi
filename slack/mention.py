import logging
import re
from dataclasses import dataclass

from dacite import from_dict
from openapi.chatgpt import login, chatbot
from slack import slack
from slackers.hooks import events


@dataclass(frozen=True)
class MentionEvent:
    client_msg_id: str
    type: str
    text: str
    user: str
    ts: str
    team: str
    channel: str
    event_ts: str


@dataclass(frozen=True)
class Mention:
    token: str
    team_id: str
    api_app_id: str
    type: str
    event_id: str
    event_time: int
    event: MentionEvent


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
