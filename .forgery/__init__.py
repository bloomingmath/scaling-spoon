from typing import Callable

def _exec_forgery_template(func_name: str="wrapped_function", annotation: dict= {}) -> str:
    import_statement = "import forge\n"

    def keyword_parameter_statement(name: str, arguments: dict) -> str:
        if "type" in arguments.keys():
            if arguments.get("optional"):
                if "default" in arguments.keys():
                    return f"forge.kwo('{name}', type=Optional[annotations['{name}']['type']], default=annotations['{name}']['default'])"
                else:
                    return f"forge.kwo('{name}', type=Optional[annotations['{name}']['type']], default=None)"
            else:
                if "default" in arguments.keys():
                    return f"forge.kwo('{name}', type=annotations['{name}']['type'], default={repr(arguments['default'])})"
                else:
                    return f"forge.kwo('{name}', type=annotations['{name}']['type'])"
        else:
            if "default" in arguments.keys():
                return f"forge.kwo('{name}', default={arguments['default']})"
            else:
                return f"forge.kwo('{name}')"

    parameters = "".join(f"\t{keyword_parameter_statement(key, value)},\n" for key, value in annotation.items())
    decorator_statement = import_statement + "@forge.sign(\n" + parameters + f")\nasync def {func_name}(**kwargs):\n\treturn await func(**kwargs)"
    return decorator_statement


def async_kwarg_wrap(func, annotations: dict):
    from typing import Optional
    d = {"func": func, "annotations": annotations, "Optional": Optional}
    exec(_exec_forgery_template(func.__name__, annotations), d)
    return d.get(func.__name__) or d["wrapped_function"]

def async_kwargs_wrap_decorator(annotations: dict = {}, context: dict = {}, name: str = None) -> Callable:
    def wrapper(func):
        from typing import Optional
        func_name = name or func.__name__
        exec_globals = {"func": func, "annotations": annotations, "Optional": Optional}
        exec_globals.update(context)
        exec(_exec_forgery_template(func_name, annotations), exec_globals)
        return exec_globals.get(func_name) or exec_globals.get("wrapped_function")
    return wrapper
