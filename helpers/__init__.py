from .encryption import generate_salt, generate_serial, hash_password, verify_password
from blinker import signal
from starlette.requests import Request


def redirect_url(request, default="/"):
    """Gives a default url unless a 'next' query parameter comes with the request."""
    try:
        url = request.query_params["next"]
        assert isinstance(url, str)
        assert len(url) > 0
        assert url[0] == "/"
    except (AttributeError, KeyError, AssertionError):
        url = None
    if url:
        return url
    else:

        return default


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
