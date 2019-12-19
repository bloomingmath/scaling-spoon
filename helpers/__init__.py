from .encryption import generate_salt, generate_serial, hash_password, verify_password


def redirect_url(request, default="/"):
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
