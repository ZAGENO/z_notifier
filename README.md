# Z-Notifier
Zageno Slack notification system

## Purpose
Notifications API to send messages via Slack webhook URLs.

### Motivation
Business logic centralisation.

If we send slack messages, no matter where from or to whom, 
the message should be customised, not the logic.

With this small implementation, I want to prove that having 
a bigger team is enough reason to split packages having logic, tests, documentation, and an assigned maintainer
a better choice in order to assure quality, stability, and accountability.

It's easier to focus and generalise, and harder to create inconvenient coupled logic.

Each individual project might grow with time. Having individual projects
makes easier to keep them clean.

In addition, code collisions and logic conflicts will be less likely as 
we see the team and business grow.

### To be considered
Slack provides public URLs to submit message requests.
This means we could post messages to any Slack organization, 
not only ours.

For instance, if an Organization had a Slack URL,
we could send instant notifications direct to the users for 
the cases we consider appropriate.

### Open Source
I believe that writing code ready for open source release
encourages the developer to deliver a higher quality work, having to respect
community standards by increasing the project's transparency and exposition to the world.

## Installation
`pip install git+ssh://git@github.com/ZAGENO/z_notifier.git@0.3.2`

## Basic Usage
```python
from z_notifier import SlackMessage, SlackNotifier

message = SlackMessage()
message.webhook_url = 'https://hooks.slack.com/services/some-channel-id'
message.header = 'Some header string'
message.footer = 'Some footer string'  # optional
message.footer_icon = 'https://platform.slack-edge.com/img/default_application_icon.png'  # optional

# you can add multiple attachments
message.attach(
    pretext='Pretext msg', 
    title='Title msg', 
    text='Markdown compatible text', 
    title_link='http://some.link', # optional
    color='#33ee33'  # optional
)

SlackNotifier.send_message(message)  # check slack :)
```

## Usage as logging handler
```python
from z_notifier import register_slack_logger_handler

logger = register_slack_logger_handler(
    'https://hooks.slack.com/services/some-channel-id',
    notify_only=(MyCustomException, MyOtherCustomException,),  # optional
    config={'header': '[[My Arbitrary Header]]', 'pretext': None, 'footer': None}  # optional
)

logger.warning('something happened!')  # check slack :)
```

### Formatter Config
A basic set of options are supported to customise messages by using the argument `config` as a dictionary.

#### header
* `'__exception_class__'`
* `'__exception_msg__'`
* `'[[arbitrary text surrounded by brakets]]'`
* a valid `LogRecord` attribute name
* `None` to omit this field

#### footer
* `'__exception_class__'`
* `'[[arbitrary text surrounded by brakets]]'`
* `None` or no implementation to omit this field

#### pretext
* a valid `LogRecord` attribute name
* None (to omit this field)

## Extend your exceptions to create markdown notifications
The handler formatter will look for a method `get_slack_text()`
without arguments and returning a string implemented 
on your exceptions.
````python
from z_notifier import register_slack_logger_handler
from mylib import create_model_url, MyObject
import logging


class MyCustomException(Exception):
    def __init__(self, msg: str, myobj, level: int = logging.ERROR, exceptions=None):
        self.msg = msg
        self.myobj = myobj
        self.level = level
        self.exceptions = exceptions

    @property
    def slack_text(self):
        """Return a string to be used as payload text"""
        return f'This is a *Markdown* message with link to <{create_admin_url(self.myobj)}|{self.myobj}>'

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


logger = register_slack_logger_handler(
    webhook_url='https://hooks.slack.com/services/some-channel-id', 
    config={
        'header': '__exception_msg__'
    },
    notify_only=(MyCustomException,),
)

try:
    myobj = MyObject()
    raise MyCustomException(myobj)
except MyCustomException as e:
    logger.exception(e)  # check slack :)
except Exception as e:
    logger.exception(e)  # no message on slack
````
