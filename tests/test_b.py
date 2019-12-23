import pytest
from async_asgi_testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_profile():
    response = await client.post("/signin", form={"username": "user", "password": "pass"})
    response = await client.get("/profile")
    pass

