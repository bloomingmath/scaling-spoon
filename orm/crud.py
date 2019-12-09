import pony.orm.core
from . import models

def create_operation_factory(model_name, schema):
    def func(db: pony.orm.core.Database, info: schema):
        ormmodel = getattr(db, model_name)
        model = getattr(models, model_name)
        if hasattr(model, "gnr"):
            info = model.gnr(**info)
        return ormmodel(**info)
    func.__name__ = f"create_{model_name.lower()}"
    return func

def get_operation_factory(model_name, schema):
    def func(db: pony.orm.core.Database, info: schema):
        return getattr(db, model_name).get(**info)
    func.__name__ = f"get_{model_name.lower()}"
    return func

def query_operation_factory(model_name, schema):
    def func(db: pony.orm.core.Database, info: schema):
        return getattr(db, model_name).select(**info)
    func.__name__ = f"query_{model_name.lower()}"
    return func

def update_operation_factory(model_name, get_schema, put_schema):
    def func(db: pony.orm.core.Database, get_info: get_schema, put_info: put_schema):
        print("update_operation", model_name)
        obj = getattr(db, model_name).get(**get_info)
        print(" > get", get_info, " -> ", obj)
        obj.set(**put_info)
        return obj
    func.__name__ = f"update_{model_name.lower()}"
    return func