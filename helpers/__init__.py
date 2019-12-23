from blinker import signal
from starlette.requests import Request

from .encryption import generate_salt
from .encryption import generate_serial
from .encryption import hash_password
from .encryption import verify_password


def flash(request, message, category):
    """Signals that a flash message has been dispatched. Somewhere else, the receiver with catch the signal."""
    signal("message-flash").send(request.app, message=message, category=category)


def load_flashes(sender, **kwargs):
    """This is the 'message-flash' signal receiver. It store (message, category) tuple in app's context_store."""
    message = str(kwargs.get("message", "¿¿¿ ... ???"))
    category = kwargs.get("category", "primary")
    flashes = sender.context_store.get("flashes", [])
    flashes.append((message, category))
    sender.context_store["flashes"] = flashes


# This function will be a depends in some routes, so request argument must be annotated to be type Request
def get_message_flashes(request: Request):
    """Pop out every message from app.context_store['flashes'] and return them as a list."""
    flashes = request.app.context_store.get("flashes", [])
    request.app.context_store["flashes"] = []
    return flashes
