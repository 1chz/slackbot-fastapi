from dataclasses import dataclass


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
