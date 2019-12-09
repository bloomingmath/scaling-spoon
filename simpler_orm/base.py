from pydantic import create_model
import inspect
import typing

class Model:
    @classmethod
    def pydmod(cls, operation: str):
        model_name = cls.__name__
        print(f"Generating {operation} {model_name}")
        if operation == "create":
            # print("Generatin create pydmod for", cls)
            fields = inspect.signature(cls.create_prep).parameters.keys()
            # print(" > fields", list(fields))
            kwargs = {}
            for attr in fields:
                # field = getattr(cls, attr)
                # print(dir(inspect.signature(cls.create_prep).parameters[attr]))
                annotation = inspect.signature(cls.create_prep).parameters[attr].annotation
                if annotation is inspect._empty:
                    attr_type = typing.Any
                else:
                    attr_type = annotation
                # print(" >> attr type:", attr_type)
                default = inspect.signature(cls.create_prep).parameters[attr].default
                if default is inspect._empty:
                    attr_default = Ellipsis
                else:
                    attr_default = default
                # print(" >> attr default", attr_default)
                kwargs[attr] = (attr_type, attr_default)
            return create_model(f"{model_name}{operation.capitalize()}Schema", **kwargs)
        else:
            return create_model(f"{model_name}{operation.capitalize()}Schema", {})