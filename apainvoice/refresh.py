from enum import auto, Enum
import datetime


class RefreshState(Enum):
    REFRESH = auto()
    UPTODATE = auto()


class RefreshStateMachine:
    def __init__(self, initial: RefreshState = RefreshState.REFRESH) -> None:
        self.state = initial

    def set_to_uptodate(self) -> None:
        self.state = RefreshState.UPTODATE

    def set_to_refresh(self) -> None:
        self.state = RefreshState.REFRESH

    def should_enter_refresh(self, first_upcoming_match) -> bool:
        current = datetime.datetime.now()
        if current >= first_upcoming_match:
            self.state = RefreshState.REFRESH

        return self.state is RefreshState.REFRESH
