from dataclasses import dataclass


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
