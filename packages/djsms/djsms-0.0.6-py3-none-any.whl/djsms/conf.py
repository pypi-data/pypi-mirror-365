# standard
from typing import Any

# dj
from django.conf import settings
from django.utils.functional import cached_property


class DJSMSConf(object):
    """DJSMS Conf"""

    @staticmethod
    def get_settings(key, default=None) -> Any:
        return getattr(settings, key, default)

    @cached_property
    def use_django_q(self):
        return self.get_settings("DJSMS_USE_DJANGO_Q", True)


djsms_conf = DJSMSConf()
