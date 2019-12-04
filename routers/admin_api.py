from fastapi import APIRouter
from fastapi import HTTPException
from ponydb import db_session
from starlette.status import HTTP_400_BAD_REQUEST


def make_router(db):
    router = APIRouter()

    for name, model in db.entities.items():
        def make_detail_endpoint(db_model):
            async def api_admin_detail(id: int):
                with db_session:
                    return db_model.get(id=id).to_dict()

            api_admin_detail.__name__ = f"api_admin_{name.lower()}_detail"
            return api_admin_detail

        router.add_api_route(f"/{name.lower()}/{{id}}", make_detail_endpoint(model))

        def make_read_endpoint(db_model):
            import forge
            parameter_list = [forge.kwo(name=param,
                                        type=(int if param == 'id' else str),
                                        default=None)
                              for param in ("id", "username", "email", "serial", "short", "filetype")]

            @forge.sign(*parameter_list)
            async def api_admin_read(**kwargs):
                with db_session:
                    print("kwargs", kwargs)
                    query = db_model.select()
                    print("all", list(query))
                    for key, value in kwargs.items():
                        try:
                            if value is not None:
                                query = query.filter(lambda obj: getattr(obj, key) == value)
                        except (ValueError, AttributeError):
                            pass
                    return [obj.to_dict() for obj in query]

            api_admin_read.__name__ = f"api_admin_{name.lower()}_read"
            return api_admin_read

        router.add_api_route(f"/{name.lower()}", make_read_endpoint(model))

        def make_create_endpoint(db_model):
            import forgery
            import forge
            from fastapi import Form
            create_method_signature = forge.fsignature(db_model.create)
            parameter_list = [forge.kwo(name=par.name,
                                        type=par.type,
                                        default=Form(... if par.default == forge.empty else par.default))
                              for par in create_method_signature]

            # annotations = {
            #     attr: {"optional": not getattr(db_model, attr).is_required, "type": getattr(db_model, attr).py_type,
            #            "default": Form(... if getattr(db_model, attr).is_required else None)}
            #     for attr in dir(db_model)
            #     if hasattr(getattr(db_model, attr), "is_required")
            #     and not getattr(db_model, attr).is_pk
            #     and getattr(db_model, attr).py_type in (int, str)}

            # @forgery.async_kwargs_wrap_decorator(annotations=annotations, context={"Form": Form},
            #                                      name=f"api_admin_{name.lower()}_create")
            @forge.sign(*parameter_list)
            async def api_admin_create(**kwargs):
                try:
                    with db_session:
                        db_model.create(**kwargs)
                        return {"detail": f"{name} object created."}
                except Exception as err:
                    print("Should be", db_model, kwargs)
                    print("Got error", err)
                    raise HTTPException(
                        status_code=HTTP_400_BAD_REQUEST,
                        detail=str(err),
                    )

            api_admin_create.__name__ = f"api_admin_{name.lower()}_create"
            return api_admin_create

        router.add_api_route(f"/{name.lower()}", make_create_endpoint(model), methods=["POST"])
    return router
