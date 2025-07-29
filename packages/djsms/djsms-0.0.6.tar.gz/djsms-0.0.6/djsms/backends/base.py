# standard
from typing import Any, List

# internal
from ..models import Message


class BaseBackend(object):
    """Base Backend"""

    identifier = "base"
    label = "Base"

    def __init__(self, config: dict | None = None) -> None:
        if config is None:
            config = {}
        self._config = self.validate_config(config)

    @staticmethod
    def validate_config(config: dict) -> dict:
        """
        Validate and optionally modify the given configuration.

        Args:
            config (dict): The configuration dictionary to validate.

        Returns:
            dict: The validated configuration dictionary.
        """
        return config

    def _get_config(self, name: str, default: Any = None) -> Any:
        """
        Retrieve a configuration value.

        Args:
            name (str): The name of the configuration key.
            default (Any, optional): The default value if the key is not found.

        Returns:
            Any: The configuration value or the default.
        """
        return self._config.get(name, default)

    def send(self, text: str, to: str, **kwargs: Any) -> Message:
        """
        Send a single message to one recipient.

        Args:
            text (str): The message content.
            to (str): The recipient phone number.
            **kwargs: Additional parameters.

        Returns:
            Message: The sent message object.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError

    def send_bulk(self, text: str, to: List[str], **kwargs: Any) -> Message:
        """
        Send the same message to multiple recipients.

        Args:
            text (str): The message content.
            to (List[str]): A list of recipient phone numbers.
            **kwargs: Additional parameters.

        Returns:
            Message: The sent message object.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError

    def send_schedule(
        self,
        text,
        to: str,
        year: int,
        month: int,
        day: int,
        hours: int,
        minutes: int,
        **kwargs: Any,
    ) -> Message:
        """
        Schedule a message to be sent at a specific date and time.

        Args:
            text (str): The message content.
            to (str): The recipient phone number.
            year (int): Scheduled year.
            month (int): Scheduled month.
            day (int): Scheduled day.
            hours (int): Scheduled hour.
            minutes (int): Scheduled minute.
            **kwargs: Additional parameters.

        Returns:
            Message: The scheduled message object.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError

    def send_pattern(
        self, name: str, to: str, args: List[str], **kwargs: Any
    ) -> Message:
        """
        Send a message using a predefined pattern or template.

        Args:
            name (str): The name of the pattern.
            to (str): The recipient phone number.
            args (List[str]): A list of arguments to fill in the pattern.
            **kwargs: Additional parameters.

        Returns:
            Message: The sent message object.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError

    def send_multiple(
        self, texts: List[str], recipients: List[str], **kwargs: Any
    ) -> Message:
        raise NotImplementedError

    def get_credit(self) -> int:
        """
        Get the remaining credit or quota for sending messages.

        Returns:
            int: The remaining credit.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError

    def __str__(self):
        return self.label

    def __repr__(self):
        return f"Backend(identifier={self.identifier}, label={self.label})"
