import logging
from z_notifier.slack import SlackNotifier, SlackMessage


class LoggerSlackHandler(logging.Handler):
    def emit(self, record):
        data = self.mapLogRecord(record)
        message = SlackMessage.from_dict(data)
        SlackNotifier.send_message(message=message)

    def mapLogRecord(self, record):
        payload = self.format(record)
        return payload


class LoggerSlackFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%', *, webhook_url=None):
        super().__init__(fmt, datefmt, style)
        assert webhook_url is not None, 'webhook_url must be set'
        self.webhook_url = webhook_url

    def format(self, record):
        return {
            'webhook_url': self.webhook_url,
            'header': self.get_header(record),
            'attachments': [{
                'pretext': self.get_pretext(record),
                'title': self.get_title(record),
                'text': self.get_text(record),
                'color': self.get_color(record)
            }]
        }

    @staticmethod
    def get_color(record):
        """Get colour code based on the severity level of log record"""
        if record.levelno == logging.DEBUG:
            return '#B6B8D6'
        elif record.levelno == logging.INFO:
            return '#BBDBD1'
        elif record.levelno == logging.WARNING:
            return '#D5A021'
        elif record.levelno == logging.ERROR:
            return '#EE6352'
        elif record.levelno == logging.CRITICAL:
            return '#D62828'

        return '#8F9491'

    @staticmethod
    def get_header(record):
        """Return the header of the slack message attachment, which is the severity level of log record"""
        return record.levelname

    @staticmethod
    def get_pretext(record):
        """Return the pretext of the slack message attachment, which is the exception type"""
        if isinstance(record.msg, Exception):
            return record.msg.__class__.__name__

        return record.msg

    @staticmethod
    def get_title(record):
        """Return the title of the slack message attachment, which is the string representation of the exception"""
        if isinstance(record.msg, Exception):
            return str(record.msg)

        return record.msg

    @staticmethod
    def get_text(record):
        """
        Return the text of the slack message attachment, which is the text representation of the exception.
        If the exception instance implements the method `get_slack_text`, it is used as part of the slack payload.
        """
        if isinstance(record.msg, Exception):
            if hasattr(record.msg, 'get_slack_text'):
                return getattr(record.msg, 'get_slack_text')()  # specific logic

            return repr(record.msg)

        return record.msg


class LoggerSlackFilter(logging.Filter):
    def __init__(self, name='', notify_only=None):
        self.notify_only = notify_only
        super().__init__(name=name)

    def filter(self, record):
        return record.msg.__class__ in self.notify_only


def register_slack_logger_handler(webhook_url, *, notify_only=None):
    """
    Register slack handler on logger
    :return logger
    """
    logger = logging.getLogger(__name__)
    sh = LoggerSlackHandler()
    sh.setFormatter(LoggerSlackFormatter(webhook_url=webhook_url))

    if notify_only:
        sh.addFilter(LoggerSlackFilter(notify_only=notify_only))

    sh.setLevel(logger.level)
    logger.addHandler(sh)
    return logger
