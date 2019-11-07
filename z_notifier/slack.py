import asyncio
import logging
import aiohttp
from z_notifier.async_helpers import ensure_event_loop
from z_notifier.exceptions import SlackPayloadError
from datetime import datetime
import requests


class SlackMessage:
    """
    A Slack message is composed by:
    - a main text message
    - a list of attachments (objects containing messages related to the main text)

    Each attachment can have a particular implementation and its text can be formatted
    and include rich content like links or content previews.
    """

    def __init__(self):
        self._webhook_url = None
        self._header = None
        self._footer = None
        self._footer_icon = 'https://platform.slack-edge.com/img/default_application_icon.png'
        self._attachments = []

    @classmethod
    def from_dict(cls, data: dict):
        message = cls()

        if not data.get('webhook_url') or (not data.get('header') and not data.get('attachments')):
            raise SlackPayloadError('Invalid message content.')

        message.webhook_url = data.get('webhook_url')
        message.header = data.get('header')

        if 'footer' in data:
            message.footer = data.get('footer')

        if 'footer_icon' in data:
            message.footer_icon = data.get('footer_icon')

        if 'attachments' in data and data.get('attachments'):
            for attachment in data.get('attachments'):
                message.attach(**attachment)

        return message


    @property
    def webhook_url(self):
        if not self._webhook_url:
            raise SlackPayloadError('No webhook_url is set.')
        return self._webhook_url

    @webhook_url.setter
    def webhook_url(self, webhook_url: str):
        if not webhook_url:
            raise SlackPayloadError('Webhook_url must be str.')

        if not webhook_url.startswith('https://hooks.slack.com'):
            raise SlackPayloadError(f'Invalid Slack Webhook URL "{webhook_url}"')

        self._webhook_url = webhook_url

    @property
    def header(self):
        return self._header

    @header.setter
    def header(self, header: str):
        """
        Set main text message to be displayed on Slack
        """
        self._header = header

    @property
    def footer(self):
        return self._footer

    @footer.setter
    def footer(self, footer: str):
        """
        Set the footer's text displayed under every attached message
        """
        self._footer = footer

    @property
    def footer_icon(self):
        return self._footer_icon

    @footer_icon.setter
    def footer_icon(self, footer_icon: str):
        """
        Set the footer icon's URL to be displayed next to the footer text
        """
        self._footer_icon = footer_icon

    @staticmethod
    def process_text(content):
        """Return the best string representation possible"""
        if isinstance(content, Exception):
            return f'{content.__class__.__name__}: {str(content)}'

        if type(content) == str:
            return content

        if hasattr(content, '__repr__'):
            return repr(content)

        return str(content)

    def attach(self, *, pretext: str, title: str, text: str, title_link: str = None, color: str = None):
        """
        This method adds one attachment to the Slack message.
        :param pretext: plain text
        :param title: plain text
        :param text: can be rich text in Markdown format
        :param title_link: optional URL to make the title a link
        :param color: colour code in hex format (e.g. #33ee33)
        """
        self._attachments.append({
            'mrkdwn': True,
            'color': color,
            'pretext': pretext,
            'title': title,
            'title_link': title_link,
            'text': self.process_text(text),
            'footer': self._footer,
            'footer_icon': self._footer_icon,
            'ts': datetime.now().timestamp()
        })

    @property
    def payload(self):
        """
        This method returns the payload expected by Slack.
        Header is required, otherwise a SlackPayloadError is raised.
        """
        if not self.header and not self._attachments:
            raise SlackPayloadError('Header or attachments are required.')

        return {
            'text': self.header,
            'attachments': self._attachments
        }

    def is_valid(self):
        """Return True if all required data by Slack is set"""
        if not self.webhook_url:
            return False

        if not self.header and not self._attachments:
            return False

        return True


class SlackNotifier:
    def __init__(self, asynchronous=False, event_loop=None):
        self.asynchronous = asynchronous
        if self.asynchronous:
            if not event_loop:
                self.event_loop = ensure_event_loop()
                asyncio.set_event_loop(self.event_loop)
            else:
                self.event_loop = event_loop
            self.event_loop.set_exception_handler(self.handle_exception)

    @staticmethod
    def sync_send_message(message: SlackMessage):
        return requests.post(message.webhook_url, json=message.payload)

    async def async_send_message(self, message: SlackMessage):
        async with aiohttp.ClientSession(loop=self.event_loop) as session:
            async with session.post(message.webhook_url, json=message.payload) as response:
                return await response.text()  # actually I don't need the response

    def send_message(self, message: SlackMessage):
        """
        Submit message payload to Slack API
        If asynchronous is True:
        A task is created using the event loop and returned to be executed later.
        """
        if not self.asynchronous:
            return self.sync_send_message(message)

        return self.async_send_message(message)

    @staticmethod
    async def log_exception(exception):
        logging.exception(exception)

    def handle_exception(self, context):
        msg = context.get("exception", context["message"])
        self.event_loop.call_soon(self.log_exception, msg)
