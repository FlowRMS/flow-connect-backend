from .base import EmailStrategy, WorkerSendEmailResult
from .gmail_strategy import GmailEmailStrategy
from .o365_strategy import O365EmailStrategy

__all__ = [
    "EmailStrategy",
    "GmailEmailStrategy",
    "O365EmailStrategy",
    "WorkerSendEmailResult",
]
