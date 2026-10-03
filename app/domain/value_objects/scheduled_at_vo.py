from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ScheduledAtVO:
    value: datetime

    def __post_init__(self):
        if self.value is None:
            ...

        if self.value <= datetime.now(timezone.utc):
            ...

    def __str__(self) -> str:
        return self.value.isoformat()
