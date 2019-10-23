import unittest
from z_notifier import SlackPayloadError
from z_notifier.slack import SlackMessage


class SlackMessageTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.message = SlackMessage()

        self.attachments = [
            {'pretext': 'Some pretext', 'title': 'Some title', 'text': 'Some text', 'color': None},
            {'pretext': 'Other pretext', 'title': 'Other title', 'text': 'Other text', 'color': '#33EE33'},
        ]
        self.expected_attachments = [
            dict(mrkdwn=True,
                 title_link=None,
                 footer=None,
                 footer_icon='https://platform.slack-edge.com/img/default_application_icon.png',
                 **d)
            for d
            in self.attachments
        ]

    def test_basic_message_object_has_payload(self):
        """Test that SlackMessage object is created with basic data produces valid payload"""
        self.message.webhook_url = 'https://hooks.slack.com/services/some-channel-id'
        self.message.header = 'This is a test message'

        self.assertDictEqual(self.message.payload, {
            'text': 'This is a test message',
            'attachments': []
        })

    def assert_attachments(self, attachments, expected_attachments):
        """Assert that generated attachments list looks like the expected list of attachments"""
        for att, expected_att in zip(attachments, expected_attachments):
            sorted_att = sorted(att.items())
            sorted_expected_att = sorted(expected_att.items())
            self.assertDictEqual(
                {k: v for k, v in sorted_att if k != 'ts'},
                {k: v for k, v in sorted_expected_att}
            )

    def test_message_with_multiple_attachments(self):
        """Test that SlackMessage object with multiple attachments produces valid payload"""
        self.message.header = 'Some header'

        for att in self.attachments:
            self.message.attach(**{k: v for k, v in sorted(att.items())})

        self.assert_attachments(self.message.payload['attachments'], self.expected_attachments)

    def test_message_with_no_data_raises_exception(self):
        """Test that an empty message raises exception when trying to get payload"""
        self.assertRaises(SlackPayloadError, lambda: self.message.payload)

    def test_message_with_no_webhook_url_raises_exception(self):
        """Test that an exception is raised when trying to get an unset webhook_url"""
        self.assertRaises(SlackPayloadError, lambda: self.message.webhook_url)

    def test_invalid_webhook_url_raises_exception(self):
        """Test that setting an invalid webhook_url raises an exception"""
        def set_invalid_webhook_url():
            self.message.webhook_url = 'invalid-webhook-url'

        self.assertRaises(SlackPayloadError, set_invalid_webhook_url)

    def test_message_returns_valid_payload_from_dict(self):
        """Test that a valid SlackMessage object is created from a dict and produces valid payload"""
        message = SlackMessage.from_dict({
            'webhook_url': 'https://hooks.slack.com/services/some-channel-id',
            'header': 'Some header',
            'attachments': self.attachments
        })

        self.assertEqual(message.payload['text'], 'Some header')
        self.assert_attachments(message.payload['attachments'], self.expected_attachments)

    def test_message_from_invalid_dict_raises_exception(self):
        """Test that an exception is raised when trying to create a SlackMessage with an invalid dictionary"""
        self.assertRaises(SlackPayloadError, SlackMessage.from_dict, {
            'webhook_url': 'https://hooks.slack.com/services/some-channel-id',
            'invalid': 'dict'
        })
