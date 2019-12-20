import pytest
from async_asgi_testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_app_is_online():
    """First of all, check if the app can run."""
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_wrong_login():
    """When posting wrong signin information, you are redirected to the mainpage and a warning message is flashed."""
    response = await client.post("/signin", form={"username": "wrong name", "password": "pass"})
    # assert response.status_code == 303
    # response = await client.send(response.next)
    assert response.status_code == 200
    assert "Benvenut@ Eternauta" in response.text
    assert "Utente non riconosciuto." in response.text


@pytest.mark.asyncio
async def test_signup_password_mismatch():
    """When posting signup form with passwords that don't match, you are stuck to the same page, but a warning signal
    is flashed """
    response = await client.post("/signup", form={
        "username": "user",
        "email": "user@example.com",
        "password": "pass",
        "repassword": "different pass",
    })
    assert response.status_code == 200
    assert "Registrati compilando questo modulo." in response.text
    assert "Le password devono coincidere." in response.text


@pytest.mark.asyncio
async def test_next_query_parameter_redirect():
    """When posting with a 'next' query parameter, you are redirected to that url if a redirection occurs."""
    response = await client.post("/signup?next=/accident", form={
        "username": "user",
        "email": "user@example.com",
        "password": "pass",
        "repassword": "pass",
    })
    assert response.status_code == 404
    response = await client.post("/signup?next=/", form={
        "username": "user2",
        "email": "user2@example.com",
        "password": "pass",
        "repassword": "pass",
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_flash_messaging():
    """When server flashes a message, it appears in the next response, just one time."""
    response = await client.post("/signup", form={"username": "user", "email": "user@example.com", "password": "pass",
                                            "repassword": "nopass"})
    assert response.status_code == 200
    assert "Guacamole!" in response.text
    response = await client.get("/")
    assert "Guacamole!" not in response.text
