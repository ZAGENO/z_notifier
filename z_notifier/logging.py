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
    def __init__(self, fmt=None, datefmt=None, style='%', *, webhook_url=None, config=None):
        super().__init__(fmt, datefmt, style)
        assert webhook_url is not None, 'webhook_url must be set'
        self.webhook_url = webhook_url
        self.config = config or {}

    def format(self, record):
        return {
            'webhook_url': self.webhook_url,
            'header': self.get_header(record),
            'footer': self.get_footer(record),
            'footer_url': self.get_footer_url(),
            'attachments': self.get_attachments(record)
        }

    @staticmethod
    def get_color(levelno):
        """Get colour code based on the severity level of log record"""
        if levelno == logging.DEBUG:
            return '#B6B8D6'
        elif levelno == logging.INFO:
            return '#BBDBD1'
        elif levelno == logging.WARNING:
            return '#D5A021'
        elif levelno == logging.ERROR:
            return '#EE6352'
        elif levelno == logging.CRITICAL:
            return '#D62828'

        return '#8F9491'

    def get_header(self, record):
        """
        Return the header of the slack message attachment
        Configuration key is prioritised in case it's implemented:
        - __exception_class__: exception class name
        - __exception_msg__: exception message string
        - [[arbitrary text]]: arbitrary text
        - <valid logging.LogRecord attribute>
        """
        if 'header' in self.config:
            if self.config.get('header') == '__exception_class__' and isinstance(record.msg, Exception):
                return record.msg.__class__.__name__
            elif self.config.get('header') == '__exception_msg__' and isinstance(record.msg, Exception):
                return getattr(record.msg, 'msg', str(record.msg))
            elif self.config.get('header').startswith('[[') and self.config.get('header')[-2:] == ']]':
                return self.config.get('header')[2:-2]
            elif hasattr(record, self.config['header']):
                return getattr(record, self.config['header'])

        return record.msg

    def get_footer(self, record):
        """
        Return the footer of the slack message
        Configuration key is prioritised in case it's implemented:
        - __exception_class__: exception class name
        - [[arbitrary text]]: arbitrary text

        No footer is returned if it's not configured.
        """
        if 'footer' in self.config:
            if self.config.get('footer') == '__exception_class__' and isinstance(record.msg, Exception):
                return record.msg.__class__.__name__
            elif self.config.get('footer').startswith('[[') and self.config.get('footer')[-2:] == ']]':
                return self.config.get('footer')[2:-2]

        return None

    def get_footer_url(self):
        """
        Return the footer icon URL for the slack message's footer
        This field will return None if footer isn't set up.
        """
        if 'footer' in self.config and 'footer_url' in self.config:
            return self.config.get('footer_url')

    def get_pretext(self, record):
        """Return the pretext of the slack message attachment"""
        if 'pretext' in self.config:
            if not self.config.get('pretext'):
                return None

            return getattr(record, self.config['pretext'])

        return record.levelname

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

            return str(record.msg)

        return record.msg

    def get_attachments(self, record):
        """
        Return a list of attachments to be used as part of the slack message payload.
        If record.msg is an exception implementing a *slack_attachment_payloads* property method
        the list of attachments is generated from it,
        otherwise a list with one element based on the record is returned.

        Attributes read if implemented:
        - slack_attachment_payloads
        - slack_pretext
        - slack_text
        - slack_level
        """
        if not hasattr(record.msg, 'slack_attachment_payloads'):
            return [{
                'pretext': self.get_pretext(record),
                'title': self.get_title(record),
                'text': self.get_text(record),
                'color': self.get_color(record.levelno)
            }]

        return [
            {
                'pretext': getattr(e, 'slack_pretext', None),
                'title': e.msg,
                'text': getattr(e, 'slack_text', None),
                'color': self.get_color(getattr(e, 'slack_level', logging.ERROR))
            }
            for e
            in getattr(record.msg, 'slack_attachment_payloads', [])
        ]


class LoggerSlackFilter(logging.Filter):
    def __init__(self, name='', notify_only=None):
        self.notify_only = notify_only
        super().__init__(name=name)

    def filter(self, record):
        return record.msg.__class__ in self.notify_only


def register_slack_logger_handler(webhook_url, *, notify_only=None, config=None):
    """
    Register slack handler on logger
    :return logger
    """
    logger = logging.getLogger(__name__)
    sh = LoggerSlackHandler()
    sh.setFormatter(LoggerSlackFormatter(webhook_url=webhook_url, config=config))

    if notify_only:
        sh.addFilter(LoggerSlackFilter(notify_only=notify_only))

    sh.setLevel(logger.level)
    logger.addHandler(sh)
    return logger
