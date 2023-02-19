import logging
from dataclasses import dataclass
from typing import Tuple

from auth.auth import is_distributor
from dacite import from_dict
from error.distribution import DistributionAbortError
from slack import slack
from slackers.hooks import actions


@dataclass(frozen=True)
class Container:
    type: str
    message_ts: str
    channel_id: str


@dataclass(frozen=True)
class Action:
    action_ts: str
    action_id: str
    value: str


@dataclass(frozen=True)
class ActionUsers:
    id: str
    username: str
    name: str
    team_id: str


@dataclass(frozen=True)
class ActionEvent:
    type: str
    container: Container
    actions: list[Action]
    user: ActionUsers


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

    if not is_distributor(user.id):
        slack.chat_postMessage(
            mrkdwn=True,
            channel=container.channel_id,
            text=f"🚫 *<@{user.id}>님은 배포 권한이 없어요. 관리자에게 ID `{user.id}`를 전달해 주세요*",
        )
        raise DistributionAbortError("User is not authorized to release.")

    slack.chat_delete(channel=container.channel_id, ts=container.message_ts)

    return user, container
