import unittest
import logging
from unittest.mock import patch
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
            'header': 'Log Record Message',
            'attachments': [
                {
                    'color': '#D5A021',
                    'pretext': 'WARNING',
                    'title': 'Log Record Message',
                    'text': 'Log Record Message'
                }
            ]
        })

    @patch('z_notifier.SlackNotifier.send_message')
    def test_register_handler_notify_only(self, mock_send_message):
        """Test that handler registered with notify_only notifies only those types of exceptions"""
        logger = register_slack_logger_handler(self.webhook_url, notify_only=(ValueError,))
        logger.handlers = [logger.handlers[-1]]  # remove all other handlers for this test
        logger.warning('some warning')
        logger.exception(ValueError('some value error'))  # only this one should be emitted
        logger.exception(KeyError('some key error'))

        self.assertEqual(mock_send_message.call_count, 1)

    def test_formatter_accepts_config(self):
        """Test that LoggerSlackFormatter returns payload using config when it's passed as argument"""
        log_record = logging.LogRecord('name', logging.DEBUG, None, None, 'some msg', None, None)
        formatter = LoggerSlackFormatter(webhook_url=self.webhook_url, config={'pretext': None})
        formatted = formatter.format(log_record)

        self.assertEqual(formatted['attachments'][0]['pretext'], None)

        formatter = LoggerSlackFormatter(webhook_url=self.webhook_url, config={'pretext': 'msg'})
        formatted = formatter.format(log_record)

        self.assertEqual(formatted['attachments'][0]['pretext'], 'some msg')

        formatter = LoggerSlackFormatter(webhook_url=self.webhook_url, config={'header': '__exception_class__'})
        log_record = logging.LogRecord('name', logging.DEBUG, None, None, ValueError('some value error'), None, None)
        formatted = formatter.format(log_record)

        self.assertEqual(formatted['header'], 'ValueError')

        formatter = LoggerSlackFormatter(webhook_url=self.webhook_url, config={'header': '[[some arbitrary header]]'})
        formatted = formatter.format(log_record)

        self.assertEqual(formatted['header'], 'some arbitrary header')
