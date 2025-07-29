class BaseSMSError(Exception):
    """Base SMS Error"""


class SMSError(BaseSMSError):
    """SMS Error"""


class SMSImproperlyConfiguredError(SMSError):
    """SMS Improperly Configured Error"""


class SMSBackendDoesNotExistError(SMSError):
    """SMSBackend Does Not Exist Error"""
