from dataclasses import dataclass

from auth.auth import is_distributor
from dacite import from_dict
from slack import slack
from slackers.hooks import commands


@dataclass(frozen=True)
class SlashCommand:
    channel_id: str
    command: str
    response_url: str
    team_id: str
    text: str
    token: str
    trigger_id: str
    user_id: str
    user_name: str


@commands.on("release")
async def handle_command_release(bytestream: dict) -> None:
    command: SlashCommand = from_dict(data=bytestream, data_class=SlashCommand)

    if not is_distributor(command.user_id):
        slack.chat_postMessage(
            mrkdwn=True,
            channel=command.channel_id,
            text=f"🚫 *<@{command.user_id}>님은 배포 권한이 없어요. 관리자에게 ID `{command.user_id}`를 전달해주세요.*",
        )
        return

    slack.chat_postMessage(
        channel=command.channel_id,
        blocks=[
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
        ],
    )
