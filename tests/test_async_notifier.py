import asynctest
import pytest
from z_notifier import SlackNotifier, SlackMessage
from aresponses import ResponsesMockServer
from z_notifier.async_helpers import ensure_event_loop


@pytest.fixture
async def aresponses(loop):
    async with ResponsesMockServer(loop=loop) as server:
        yield server


class NotifierAsyncTestCase(asynctest.TestCase):
    def setUp(self) -> None:
        self.event_loop = ensure_event_loop()
        self.slack_notifier = SlackNotifier(asynchronous=True, event_loop=self.event_loop)

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        async with ResponsesMockServer(loop=self.event_loop) as arsps:
            arsps.add('hooks.slack.com', '/services/some-channel-id', 'post', 'ok')

            message = SlackMessage()
            message.webhook_url = 'https://hooks.slack.com/services/some-channel-id'
            message.header = 'some header'

            response = await self.slack_notifier.send_message(message)
            self.assertEqual(response, 'ok')


