import os

from subscriptions.domain.ports import Notifier

from .notifiers import ConsoleNotifier, MockNotifier


class NotifierFactory:
    @staticmethod
    def create() -> Notifier:
        env_type = os.getenv("ENV_TYPE", "MOCK").upper()
        if env_type == "REAL":
            return ConsoleNotifier()
        return MockNotifier()
