import unittest
import logging
from z_notifier import register_slack_logger_handler, LoggerSlackHandler, LoggerSlackFormatter


class SlackLoggerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.webhook_url = 'https://hooks.slack.com/services/some-channel-id'
        self.logger = register_slack_logger_handler(self.webhook_url)
        self.handler = self.logger.handlers[0]  # assume there's only slack logger handler in the list
        self.log_record = logging.LogRecord(
            name='Log Record Name',
            level=logging.WARNING,
            msg='Log Record Message',
            pathname=None,
            lineno=0,
            args=None,
            exc_info=None
        )

    def test_logger_is_registered(self):
        """Test that SlackLoggerHandler is registered as logging handler"""
        present = False
        for h in self.logger.handlers:
            if isinstance(h, LoggerSlackHandler):
                present = True
        self.assertTrue(present)

    def test_handler_has_formatter(self):
        """Test that SlackLoggerHandler uses SlackLoggerFormatter as formatter"""
        self.assertIsInstance(self.handler.formatter, LoggerSlackFormatter)

    def test_formatter_returns_slack_payload(self):
        """Test that SlackLoggerHandler.format returns a dict compatible to use with SlackMessage"""
        formatter = LoggerSlackFormatter(webhook_url=self.webhook_url)
        payload = formatter.format(self.log_record)
        self.assertDictEqual(payload, {
            'webhook_url': self.webhook_url,
            'header': 'WARNING',
            'attachments': [
                {
                    'color': '#D5A021',
                    'pretext': 'Log Record Message',
                    'title': 'Log Record Message',
                    'text': 'Log Record Message'
                }
            ]
        })
