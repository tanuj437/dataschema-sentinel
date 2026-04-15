"""Slack webhook alerter."""

from typing import Optional

from sentinel.alerts.base import BaseAlerter
from sentinel.detector.drift import DriftEvent, DriftSeverity
from sentinel.store.models import SchemaSnapshot


class SlackAlerter(BaseAlerter):
    """Alert via Slack webhook.

    TODO: Implement Slack webhook integration using slack-sdk.
    """

    def __init__(self, webhook_url: str):
        """Initialize Slack alerter.

        Args:
            webhook_url: Slack webhook URL for posting messages
        """
        self.webhook_url = webhook_url

    def alert(
        self,
        name: str,
        old_snapshot: SchemaSnapshot,
        new_snapshot: SchemaSnapshot,
        events: list[DriftEvent],
    ) -> None:
        """Send drift alert to Slack.

        Args:
            name: Schema name
            old_snapshot: Previous snapshot
            new_snapshot: Current snapshot
            events: List of drift events
        """
        raise NotImplementedError("SlackAlerter not yet implemented")
