from . import pony_models
from .base import Model


operations = ("create", "get", "select", "update", "show")


def is_model(x):
    try:
        return issubclass(x, Model)
    except TypeError:
        return False


models = filter(is_model, (getattr(pony_models, model_name) for model_name in dir(pony_models)))


def generate_pydantic_schemas(operations, models):
    print("generating_pydantic_schemas", operations, models)
    class PydanticSchemas:
        def __init__(self):
            for op in operations:
                class PydanticOperationSchemas:
                    def __init__(self):
                        for model in models:
                            print("setting", model.__name__.lower(), op)
                            setattr(self, model.__name__.lower(), model.pydmod(op))

                setattr(self, op, PydanticOperationSchemas())

    return PydanticSchemas()
