from starlette.testclient import TestClient

from main import app

client = TestClient(app)


def test_app_is_online():
    """First of all, check if the app can run."""
    response = client.get("/")
    assert response.status_code == 200


def test_wrong_login():
    """When posting wrong signin information, you are redirected to the mainpage and a warning message is flashed."""
    response = client.post("/signin", data={"username": "wrong name", "password": "pass"})
    assert response.status_code == 303
    response = client.send(response.next)
    assert response.status_code == 200
    assert response.url == "http://testserver/"
    assert "Utente non riconosciuto." in response.content.decode("utf-8")


def test_signup_password_mismatch():
    """When posting signup form with passwords that don't match, you are stuck to the same page, but a warning signal
    is flashed """
    response = client.post("/signup", data={
        "username": "user",
        "email": "user@example.com",
        "password": "pass",
        "repassword": "different pass",
    })
    assert response.status_code == 303
    response = client.send(response.next)
    assert response.status_code == 200
    assert response.url == "http://testserver/signup"
    assert "Le password devono coincidere." in response.content.decode("utf-8")


def test_next_query_parameter_redirect():
    """When posting with a 'next' query parameter, you are redirected to that url if a redirection occurs."""
    response = client.post("/signup?next=/accident", data={
        "username": "user",
        "email": "user@example.com",
        "password": "pass",
        "repassword": "pass",
    })
    assert response.status_code == 303
    assert response.headers["location"] == "/accident"
    response = client.send(response.next)
    assert response.url == "http://testserver/accident"


def test_flash_messaging():
    """When server flashes a message, it appears in the next response, just one time."""
    response = client.post("/signup", data={"username": "user", "email": "user@example.com", "password": "pass",
                                            "repassword": "nopass"})
    assert response.status_code == 303
    response = client.get("/")
    assert response.status_code == 200
    assert "Guacamole!" in response.content.decode("utf-8")
    response = client.get("/")
    assert "Guacamole!" not in response.content.decode("utf-8")
