import typing
from pydantic import create_model
from pony import orm


class Scope:
    def __init__(self, s: str):
        self.scp = s.translate(s.maketrans("", "", "!?"))
        self.is_required = "?" not in s
        self.is_optional = "?" in s
        self.is_unique = "!" in s


class Field:
    def __init__(self, scpi: str, gnr: typing.Optional[typing.Tuple[typing.Callable, typing.Dict]] = None, **kwargs):
        self.scps = {sc.scp: sc for sc in [Scope(s) for s in scpi.split()]}
        if gnr:
            self.generator = gnr[0]
            self.gen_kwargs = gnr[1]


class Str(Field):
    def __init__(self, scpi, **kwargs):
        super().__init__(scpi, **kwargs)

    def pydtype(self):
        return str

    def ormtype(self):
        assert "store" in self.scps
        scope = self.scps["store"]
        if scope.is_required:
            return orm.Required(str)
        else:
            return orm.Optional(str)


class Json(Field):
    def __init__(self, scpi, **kwargs):
        super().__init__(scpi, **kwargs)

    def pydtype(self):
        return str

    def ormtype(self):
        assert "store" in self.scps
        scope = self.scps["store"]
        if scope.is_required:
            return orm.Required(orm.Json)
        else:
            return orm.Optional(orm.Json)


class Ref(Field):
    def __init__(self, to, scpi, **kwargs):
        super().__init__(scpi, **kwargs)
        self.to = to

    def pydtype(self):
        return int

    def ormtype(self):
        assert "store" in self.scps
        scope = self.scps["store"]
        if scope.is_required:
            return orm.Required(self.to)
        else:
            return orm.Optional(self.to)


class Set(Field):
    def __init__(self, of, scpi, reverse=None, **kwargs):
        super().__init__(scpi, **kwargs)
        self.of = of
        self.reverse = reverse

    def pydtype(self):
        return typing.Set[int]

    def ormtype(self):
        assert "store" in self.scps
        if self.reverse:
            return orm.Set(self.of, reverse=self.reverse)
        else:
            return orm.Set(self.of)


class Model:
    @classmethod
    def pydmod(cls, scope):
        model_name = cls.__name__
        if scope == "create":
            import inspect
            # print("Generatin create pydmod for", cls)
            fields = inspect.signature(cls.gnr).parameters.keys()
            # print(" > fields", list(fields))
            kwargs = {}
            for attr in fields:
                # field = getattr(cls, attr)
                # print(dir(inspect.signature(cls.gnr).parameters[attr]))
                annotation = inspect.signature(cls.gnr).parameters[attr].annotation
                if annotation is inspect._empty:
                    attr_type = typing.Any
                else:
                    attr_type = annotation
                # print(" >> attr type:", attr_type)
                default = inspect.signature(cls.gnr).parameters[attr].default
                if default is inspect._empty:
                    attr_default = Ellipsis
                else:
                    attr_default = default
                # print(" >> attr default", attr_default)
                kwargs[attr] = (attr_type, attr_default)
            return create_model(f"{model_name}{scope.capitalize()}Schema", **kwargs)
        fields = [attr
                  for attr in dir(cls)
                  if isinstance(getattr(cls, attr), Field)
                  and scope in getattr(cls, attr).scps]
        kwargs = {}
        for attr in fields:
            field = getattr(cls, attr)
            kwargs[attr] = (field.pydtype(), ... if field.scps[scope].is_required else None)
        if scope == "get":
            kwargs["id"] = (int, None)
        return create_model(f"{model_name}{scope.capitalize()}Schema", **kwargs)

    @classmethod
    def ormmodk(cls, db):
        model_name = cls.__name__
        kwargs = {
            "_table": model_name.lower(),
            "id": orm.PrimaryKey(int, auto=True),
        }
        fields = [attr for attr in dir(cls)
                  if isinstance(getattr(cls, attr), Field)
                  and "store" in getattr(cls, attr).scps]
        for attr in fields:
            field = getattr(cls, attr)
            kwargs[attr] = field.ormtype()
        return kwargs
        # model = type(model_name.capitalize(), (db.Entity,), kwargs)
        # print("Generated", model)
        # return model
