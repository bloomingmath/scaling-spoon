import pytest
from async_asgi_testclient import TestClient
from main import app, mc, db_session

client = TestClient(app)


@pytest.mark.asyncio
async def test_node_group_relationship():
    with db_session:
        n1 = mc.Node.operations.fetch(dict(short="first"))
        g = list(n1.groups)[0]
        assert len(list(g.nodes)) == 3
    assert True
