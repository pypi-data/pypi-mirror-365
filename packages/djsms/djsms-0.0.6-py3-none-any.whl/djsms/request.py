# requests
import requests

# internal
from .conf import djsms_conf
from .models import Message
from .hooks import send_message_hook
from .consts import HTTP_200_OK, HTTP_201_CREATED
from .errors import SMSError, SMSImproperlyConfiguredError

# djq
try:
    from django_q.tasks import async_task
except ImportError:
    async_task = None


def _req(method: str, url: str, **kwargs) -> requests.Response:
    try:
        res = getattr(requests, method)(url, **kwargs)
    except Exception as e:
        raise SMSError(str(e))
    if res.status_code not in [HTTP_200_OK, HTTP_201_CREATED]:
        raise SMSError()
    return res


def get(url: str, **kwargs) -> requests.Response:
    return _req("get", url, **kwargs)


def post(url: str, **kwargs) -> requests.Response:
    return _req("post", url, **kwargs)


def send_sync_message(text: str, recipient: str, url: str, **kwargs) -> Message:
    post(url, **kwargs)
    return Message.objects.create(
        text=text,
        recipient=recipient,
        status=Message.SUCCESS,
        data={"url": url, **kwargs},
    )


def send_async_message(text: str, recipient: str, url: str, **kwargs) -> Message:
    if async_task is None:
        raise SMSImproperlyConfiguredError("django_q should be installed first.")
    task_id = async_task(post, url, **kwargs, hook=send_message_hook)  # noqa
    return Message.objects.create(
        task_id=task_id,
        text=text,
        recipient=recipient,
        status=Message.PENDING,
        data={"url": url, **kwargs},
    )


def send_message(text: str, recipient: str, url: str, **kwargs) -> Message:
    if djsms_conf.use_django_q:
        return send_async_message(text, recipient, url, **kwargs)
    else:
        return send_sync_message(text, recipient, url, **kwargs)
