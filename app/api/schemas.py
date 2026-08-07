from dataclasses import dataclass, asdict


@dataclass
class ChatResponse:

    success: bool

    intent: str

    answer: str

    scheme: str | None = None

    location: str | None = None

    def to_dict(self):

        return asdict(self)