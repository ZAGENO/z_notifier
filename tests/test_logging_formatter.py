import unittest
import logging

from z_notifier import LoggerSlackFormatter


class ExtendedException(Exception):
    def __init__(self, msg: str, level: int = logging.ERROR, exceptions=None):
        self.msg = msg
        self.level = level
        self.exceptions = exceptions

    @property
    def slack_text(self):
        """Return a string to be used as payload text"""
        return 'Some error message'

    @property
    def slack_attachment_payloads(self):
        """Return a list of exceptions to be used as payload attachments"""
        return self.exceptions or []

    @property
    def slack_pretext(self):
        """Return a string used as pretext"""
        return 'Some pretext'

    @property
    def slack_level(self):
        """Error level given by logging package"""
        return self.level

    def __str__(self):
        return self.msg


class LoggingFormatterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.webhook_url = 'https://hooks.slack.com/services/some-channel-id'
        self.formatter = LoggerSlackFormatter(webhook_url=self.webhook_url, config={
            'header': '__exception_msg__',
            'footer': '[[Some footer]]',
            'footer_url': 'https://cataas.com/cat'
        })

    def test_formatting_exception_without_methods(self):
        """Test that a payload is created out of a normal exception"""
        log_records = [
            logging.LogRecord(name='error1',
                              level=logging.WARNING,
                              pathname=__file__,
                              lineno=0,
                              msg=Exception('Something happened'),
                              args=None,
                              exc_info=None),
            logging.LogRecord(name='error2',
                              level=logging.ERROR,
                              pathname=__file__,
                              lineno=0,
                              msg=Exception('Something else happened'),
                              args=None,
                              exc_info=None),
        ]

        payloads = [
            self.formatter.format(record)
            for record
            in log_records
        ]

        self.assertEqual(len(payloads), len(log_records))
        self.assertEqual(len(payloads[0]['attachments']), 1)
        self.assertIn('header', payloads[0])
        self.assertEqual(payloads[0]['header'], 'Something happened')
        self.assertEqual(payloads[0]['footer'], 'Some footer')
        self.assertEqual(payloads[1]['footer'], 'Some footer')
        self.assertEqual(payloads[0]['footer_url'], 'https://cataas.com/cat')
        self.assertEqual(payloads[1]['footer_url'], 'https://cataas.com/cat')
        self.assertEqual(payloads[0]['attachments'][0]['text'], 'Something happened')
        self.assertEqual(payloads[0]['attachments'][0]['color'], '#D5A021')
        self.assertEqual(payloads[1]['attachments'][0]['text'], 'Something else happened')
        self.assertEqual(payloads[1]['attachments'][0]['color'], '#EE6352')

    def test_formatting_exception_with_methods_multiple(self):
        """Test that a payload is created using the correct properties out of an extended exception"""
        exceptions = [
            ExtendedException('Something happened', level=logging.DEBUG),
            ExtendedException('Something else happened', level=logging.INFO),
        ]
        log_record = logging.LogRecord(name='error-with-attachments',
                                       level=logging.WARNING,
                                       pathname=__file__,
                                       lineno=0,
                                       msg=ExtendedException('Multiple errors', exceptions=exceptions),
                                       args=None,
                                       exc_info=None)
        payload = self.formatter.format(log_record)

        self.assertEqual(len(payload['attachments']), 2)
        self.assertIn('header', payload)
        self.assertEqual(payload['header'], 'Multiple errors')
        self.assertEqual(payload['footer'], 'Some footer')
        self.assertEqual(payload['footer_url'], 'https://cataas.com/cat')
        self.assertEqual(payload['attachments'][0]['color'], '#B6B8D6')
        self.assertEqual(payload['attachments'][1]['color'], '#BBDBD1')
        self.assertEqual(payload['attachments'][0]['pretext'], 'Some pretext')
        self.assertEqual(payload['attachments'][1]['pretext'], 'Some pretext')
        self.assertEqual(payload['attachments'][0]['title'], 'Something happened')
        self.assertEqual(payload['attachments'][1]['title'], 'Something else happened')
