import platform
from datetime import datetime

from .kafka_producer import Producer
from .. import WeDeliverCore
from wedeliver_core.helpers.topics import Topics

def send_critical_error(message, channel=None):
    channel = channel or "critical-errors"
    send_notification_message(
        channel=channel,
        title="critical",
        color="#df0000",
        message=message,
        emoji=":pleading_face:"
    )


def send_notification_message(
        message, channel="logs", title="Log", color="#32a4a7", emoji=":dizzy_face:"
):
    app = WeDeliverCore.get_app()
    channel = "eng-{0}-{1}".format(
        app.config.get("FLASK_ENV")
        if app.config.get("FLASK_ENV") == "production"
        else "development",
        channel,
    )
    datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    message = "Node: {0}\nEnv:{3}\nDate: {1}\n{2}".format(
        platform.node(),datetime_now, message, str(app.config.get("FLASK_ENV"))
    )
    data = {
        "notification_method": "slack",
        "payload": {
            "channel": channel,
            "title": "New {0} in {1} Service".format(
                title, str(app.config.get("SERVICE_NAME"))
            ),
            "text": message,
            "color": color,
            "icon_emoji": emoji,
        },
    }
    app.logger.debug(data)
    Producer().send_topic(topic=Topics.INTERNAL_NOTIFICATION_MESSAGE.value, datajson=data)
