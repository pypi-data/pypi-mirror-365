# standard
import re
from datetime import timezone
from zoneinfo import ZoneInfo
from typing import Any, List, Dict

# dj
from django.utils import timezone

# jdatetime
import jdatetime

# internal
from .. import request
from ..models import Message
from .base import BaseBackend
from ..errors import SMSImproperlyConfiguredError


BASE_URL = "https://edge.ippanel.com/v1"


class IPPanel(BaseBackend):
    """IP Panel"""

    identifier = "ippanel"
    label = "IPPanel"

    @staticmethod
    def validate_config(config: dict) -> dict:
        token = config.get("token")
        from_number = config.get("from")
        patterns = config.get("patterns")
        # validate token
        if not token or not isinstance(token, str):
            raise SMSImproperlyConfiguredError("Invalid token.")
        # validate from_number
        if (
            not from_number
            or not isinstance(from_number, str)
            or not re.match(r"^\+98\d+$", from_number)
        ):
            raise SMSImproperlyConfiguredError("Invalid from number.")
        # validate patterns
        if patterns is not None:
            if not isinstance(patterns, list):
                raise SMSImproperlyConfiguredError("Invalid patterns.")
            for pattern in patterns:
                if not isinstance(pattern, dict) or not all(
                    key in pattern for key in ("id", "name", "body", "arg_keys")
                ):
                    raise SMSImproperlyConfiguredError("Invalid patterns")
        # return validated config
        return config

    @property
    def token(self) -> str:
        return self._get_config("token")

    @property
    def from_number(self) -> str:
        return self._get_config("from")

    @property
    def patterns(self) -> list:
        return self._get_config("patterns", [])

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": self.token, "Content-Type": "application/json"}

    @property
    def send_message_url(self) -> str:
        return self.get_url("/api/send")

    @staticmethod
    def get_url(path: str) -> str:
        return "{base_url}/{path}".format(base_url=BASE_URL, path=path)

    def _send_message(self, text: str, recipient: str, url: str, **kwargs) -> Message:
        return request.send_message(
            text, recipient, url, headers=self.headers, **kwargs
        )

    def get_pattern(self, name: str) -> dict:
        for pattern in self.patterns:
            if pattern["name"] == name:
                return pattern
        raise SMSImproperlyConfiguredError("Pattern does not exist.")

    @staticmethod
    def clean_phone_number(phone_number: str, prefix="+98") -> str:
        if not phone_number.startswith(prefix):
            if phone_number.startswith("09"):
                # remove 0 from phone_number
                phone_number = phone_number[1:]
                # join prefix to phone_number
                phone_number = "{prefix}{phone_number}".format(
                    prefix=prefix,
                    phone_number=phone_number
                )
            else:
                raise SMSImproperlyConfiguredError("Invalid recipient phone number.")
        # return cleaned phone_number
        return phone_number

    def send(self, text: str, to: str, **kwargs: Any) -> Message:
        # clean and validate phone number
        to = self.clean_phone_number(to)
        # prepare request body
        data = {
            "sending_type": "webservice",
            "from_number": self.from_number,
            "message": text,
            "params": {"recipients": [to]},
        }
        return self._send_message(text, to, self.send_message_url, json=data)

    def send_bulk(self, text: str, to: List[str], **kwargs: Any) -> Message:
        # clean and validate phone numbers
        to = [self.clean_phone_number(phone_number) for phone_number in to]
        # prepare request body
        data = {
            "sending_type": "webservice",
            "from_number": self.from_number,
            "message": text,
            "params": {"recipients": to},
        }
        return self._send_message(text, ",".join(to), self.send_message_url, json=data)

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
        # clean and validate phone number
        to = self.clean_phone_number(to)
        # get seconds from kwargs or default to 0
        seconds = kwargs.get("seconds", 0)
        # create a datetime object and convert jalali date to gregorian date
        gregorian_datetime = jdatetime.datetime(
            year=year, month=month, day=day, hour=hours, minute=minutes, second=seconds
        ).togregorian()
        # set tehran timezone on gregorian_datetime
        gregorian_datetime = gregorian_datetime.replace(tzinfo=ZoneInfo("Asia/Tehran"))
        # convert time to utc
        send_time = gregorian_datetime.astimezone(timezone.utc)
        # prepare request body
        data = {
            "sending_type": "webservice",
            "from_number": self.from_number,
            "message": text,
            "params": {"recipients": [to]},
            "send_time": send_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        # send message
        return self._send_message(text, to, self.send_message_url, json=data)

    def send_pattern(
        self, name: str, to: str, args: List[str], **kwargs: Any
    ) -> Message:
        # clean and validate phone number
        to = self.clean_phone_number(to)
        # find pattern or raise SMSImproperlyConfiguredError
        pattern = self.get_pattern(name)
        arg_keys = pattern.get("arg_keys")
        # check length of args and arg_keys
        if len(args) != len(arg_keys):
            raise SMSImproperlyConfiguredError(
                "length of args and arg_keys must be same."
            )
        # match arg_keys with args
        arguments = zip(arg_keys, args)
        # prepare request body
        data = {
            "sending_type": "pattern",
            "from_number": self.from_number,
            "code": pattern.get("id"),
            "recipients": [to],
            "params": dict(arguments),
        }
        # send message
        return self._send_message(
            pattern["body"].format(*args), to, self.send_message_url, json=data
        )

    def send_multiple(
        self, texts: List[str], recipients: List[str], **kwargs: Any
    ) -> Message:
        # clean and validate phone numbers
        recipients = [self.clean_phone_number(phone_number) for phone_number in recipients]
        # check length of texts and recipients
        if len(texts) != len(recipients):
            raise SMSImproperlyConfiguredError(
                "length of texts and recipients must be same."
            )
        # create params base on ippanel acceptable format
        params = [
            {"recipients": [recipients[item_index]], "message": texts[item_index]}
            for item_index in range(len(texts))
        ]
        # prepare request body
        data = {
            "sending_type": "peer_to_peer",
            "from_number": self.from_number,
            "params": params,
        }
        return self._send_message(
            ",".join(texts), ",".join(recipients), self.send_message_url, json=data
        )

    def get_credit(self) -> int:
        url = self.get_url("/api/payment/credit/mine")
        res = request.get(url, headers=self.headers).json()
        remain_credit = res["data"]["credit"]
        return int(remain_credit)
