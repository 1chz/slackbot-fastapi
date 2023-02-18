from dataclasses import dataclass


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
