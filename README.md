# Z-Notifier
Zageno Slack notification system

## Purpose
Notifications API to send messages via Slack webhook URLs.

### Motivation
Business logic centralisation.

If we send slack messages, no matter where from or to whom, 
the message should be customised, not the logic.

### To be considered
Slack provides public URLs to submit message requests.
This means we could post messages to any Slack organization, 
not only ours.

For instance, if an Organization had a Slack URL,
we could send instant notifications direct to the users for 
the cases we consider appropriate.

### Technical implications
My proposal goes clearly beyond the implementation of some Slack messages.

With this small implementation, I want to prove that having 
a bigger team is enough reason to
split packages having logic, tests, documentation, and an assigned maintainer
a better choice in order to assure quality, stability, and accountability.

It's easier to focus and generalise, and harder to create 
inconvenient coupled logic.

Each individual project might grow with time, having individual projects
makes easier to keep them clean.

In addition, code collisions and logic conflicts will be less likely as 
we see the team and business grow.

### Open Source
I believe that writing code ready for open source delivery
forces the developer to deliver a higher quality work, having to respect
community standards and increasing the project's transparency and exposition to the world.

Creating separate projects for particular logic implementations is a necessary
step in this direction.

## Installation
`pip install git+https://github.com/ZAGENO/z_notifier@0.2.0`

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
    config={'header': '[[My Arbitrary Header]]', 'pretext': None}  # optional
)

logger.warning('something happened!')  # check slack :)
```

### Formatter Config
A basic set of options are supported to customise messages by using the argument `config` as a dictionary.

#### header
* `__exception_class__`
* `[[arbitrary text surrounded by brakets]]`
* a valid `LogRecord` attribute name
* None (to omit this field)

#### pretext
* a valid `LogRecord` attribute name
* None (to omit this field)

## Extend your exceptions to create markdown notifications
The handler formatter will look for a method `get_slack_text()`
without arguments and returning a string implemented 
on your exceptions.
````python
from mylib import create_model_url

class SomeException(Exception):
    def __init(self, myobj):
        self.myobj = myobj

    def get_slack_text(self):
        return f'This is a *Markdown* message with link to <{create_admin_url(self.myobj)}|{self.myobj}>'

try:
    myobj = MyObject()
    raise SomeException(myobj)
except SomeException as e:
    logger.exception(e)  # check slack :)
````
