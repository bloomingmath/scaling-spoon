from . import models

operations = ("create", "get", "select", "update", "show")


def generate_pydantic_schemas():
    class PydanticSchemas:
        def __init__(self):
            for op in operations:
                class PydanticOperationSchemas:
                    def __init__(self):
                        for model_name in models.__all__:
                            setattr(self, model_name.lower(), getattr(models, model_name).pydmod(op))

                setattr(self, op, PydanticOperationSchemas())

    return PydanticSchemas()
