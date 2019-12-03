from . import async_kwargs_wrap_decorator
import os
import pytest

if os.environ.get("SCALING_SPOON_PRODUCTION"):
    del os.environ["SCALING_SPOON_PRODUCTION"]


@pytest.mark.asyncio
async def test_forgery():
    fake_annotations = {
        "alpha": {},
        "beta": {"type": str},
        "gamma": {"default": 23},
        "delta": {"type": str, "default": "some"},
        "eta": {"type": int, "optional": True},
    }

    @async_kwargs_wrap_decorator(annotations=fake_annotations)
    async def test_function(**kwargs):
        return kwargs

    assert await test_function(alpha=0, beta='23') == {'alpha': 0, 'beta': '23',
                                                       'delta': "some",
                                                       'eta': None, 'gamma': 23}


@pytest.mark.asyncio
async def test_forgery_with_context():
    import fastapi.params
    import fastapi
    fake_annotations = {
        "alpha": {},
        "beta": {"type": str},
        "gamma": {"default": 23},
        "delta": {"type": str, "default": fastapi.Form(...)},
        "eta": {"type": int, "optional": True},
    }

    @async_kwargs_wrap_decorator(annotations=fake_annotations, context={'Form': fastapi.Form})
    async def test_function(**kwargs):
        return kwargs

    print(type((await test_function(alpha=0, beta='23'))["delta"]))
    assert isinstance((await test_function(alpha=0, beta='23')), dict)
    assert "delta" in (await test_function(alpha=0, beta='23')).keys()
    assert isinstance((await test_function(alpha=0, beta='23'))["delta"], fastapi.params.Form)
