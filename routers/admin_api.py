from fastapi import APIRouter
from ponydb import std_db as db
from ponydb import db_session

router = APIRouter()

# def setup_admin_api(router, db, db_session):
for name, model in db.entities.items():
    def make_list_endpoint(model):
        async def api_admin_list():
            with db_session:
                _list = [obj.to_dict() for obj in model.select()]
            return _list

        return api_admin_list

    router.add_api_route("/{}".format(name.lower()), make_list_endpoint(model))

    def make_detail_endpoint(model):
        async def api_admin_detail(id: int):
            with db_session:
                return model.get(id=id).to_dict()

        return api_admin_detail

    router.add_api_route("/%s/{id}" % name.lower(), make_detail_endpoint(model))

    def make_create_endpoint(model):
        from fastapi import Depends
        from fastapi import Form

        required_kwargs = { kw:getattr(model, kw).py_type for kw in dir(model)
                           if hasattr(getattr(model, kw), 'is_required')
                           and getattr(model, kw).is_required
                           and not getattr(model, kw).is_pk
                            and getattr(model, kw).py_type in (int, str) }

        def async_kwarg_wrap(func, kw, kwt):
            import functools
            import forge
            d = {'func': func, 'kw': kw, 'functools': functools, 'forge':forge, 'kwt': kwt}
            pre_annotation = func.__annotations__
            exec("""
@forge.sign(
    forge.kwo('{kw}', type=kwt),
    *forge.fsignature(func)
)
async def wfunc({kw}, **kwargs):
    return "{kw} is %s... " % {kw} + await func(**kwargs)
""".format(kw=kw, kwt=kwt), d)
            d["wfunc"].__annotations__.update(pre_annotation)
            print("wfunc signature", forge.fsignature(d["wfunc"]))
            return d["wfunc"]

        async def api_admin_create():
            return "stop"

        for kw, kwt in required_kwargs.items():
            api_admin_create = async_kwarg_wrap(api_admin_create, kw=kw, kwt=kwt)

        return api_admin_create

    router.add_api_route("/%s" % name.lower(), make_create_endpoint(model), methods=["POST"])
