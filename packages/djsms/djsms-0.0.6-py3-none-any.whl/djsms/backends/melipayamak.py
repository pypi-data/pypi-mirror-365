# standard
import re
from typing import Any, List

# internal
from .. import request
from ..models import Message
from .base import BaseBackend
from ..errors import SMSImproperlyConfiguredError


BASE_URL = "https://console.melipayamak.com/api"


class MeliPayamak(BaseBackend):
    """Meli Payamak"""

    identifier = "melipayamak"
    label = "MeliPayamak"

    @staticmethod
    def validate_config(config: dict) -> dict:
        token = config.get("token")
        number = config.get("number")
        patterns = config.get("patterns")
        # validate token
        if not token or not isinstance(token, str):
            raise SMSImproperlyConfiguredError("Invalid token.")
        # validate number
        if number is not None:
            if not isinstance(number, str) or not re.match("^\d{4,}$", number):  # noqa
                raise SMSImproperlyConfiguredError("Invalid number.")
        # validate patterns
        if patterns is not None:
            if not isinstance(patterns, list):
                raise SMSImproperlyConfiguredError("Invalid patterns.")
            for pattern in patterns:
                if not isinstance(pattern, dict) or not all(
                    key in pattern for key in ("id", "name", "body")
                ):
                    raise SMSImproperlyConfiguredError("Invalid patterns")
        # return validated config
        return config

    @property
    def token(self) -> str:
        return self._get_config("token")

    @property
    def patterns(self) -> list:
        return self._get_config("patterns")

    def get_url(self, path: str) -> str:
        return f"{BASE_URL}/{path}/{self.token}"

    def get_from(self, kwargs: Any) -> str:
        return kwargs.get("from", self._get_config("from"))

    def get_udh(self, kwargs: Any) -> str:
        return kwargs.get("udh", self._get_config("udh", ""))

    def get_pattern(self, name: str) -> dict:
        patterns = self.patterns or []
        for pattern in patterns:
            if pattern["name"] == name:
                return pattern
        raise SMSImproperlyConfiguredError("Pattern does not exist.")

    def send(self, text: str, to: str, **kwargs: Any) -> Message:
        url = self.get_url("send/simple")
        data = {"text": text, "to": to, "from": self.get_from(kwargs)}
        return request.send_message(text, to, url, json=data)

    def send_bulk(self, text: str, to: List[str], **kwargs: Any) -> Message:
        url = self.get_url("send/advanced")
        data = {
            "text": text,
            "to": to,
            "from": self.get_from(kwargs),
            "udh": self.get_udh(kwargs),
        }
        return request.send_message(text, ",".join(to), url, json=data)

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
        url = self.get_url("send/schedule")
        data = {
            "message": text,
            "from": self.get_from(kwargs),
            "to": to,
            "data": f"{month}/{day}/{year} {hours}:{minutes}",
        }
        # check for period
        if "period" in kwargs:
            data["period"] = kwargs["period"]
        return request.send_message(text, to, url, json=data)

    def send_pattern(
        self, name: str, to: str, args: List[str], **kwargs: Any
    ) -> Message:
        url = self.get_url("send/shared")
        pattern = self.get_pattern(name)
        data = {"bodyId": pattern["id"], "to": to, "args": args}
        return request.send_message(pattern["body"].format(*args), to, url, json=data)

    def send_multiple(
        self, texts: List[str], recipients: List[str], **kwargs: Any
    ) -> Message:
        url = self.get_url("send/multiple")
        data = {
            "to": recipients,
            "text": texts,
            "from": self.get_from(kwargs),
            "udh": self.get_udh(kwargs),
        }
        return request.send_message(
            ",".join(texts), ",".join(recipients), url, json=data
        )

    def get_credit(self) -> int:
        url = self.get_url("receive/credit")
        res = request.get(url)
        return res.json()["amount"]
