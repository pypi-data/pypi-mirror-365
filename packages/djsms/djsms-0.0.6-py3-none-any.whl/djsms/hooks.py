# internal
from .models import Message


def send_message_hook(task) -> None:
    message = Message.objects.filter(task_id=task.id).first()
    if message:
        message.status = Message.SUCCESS if task.success else Message.FAILED
        message.save(update_fields=["status"])
