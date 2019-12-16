from importlib import import_module
from inspect import isclass
from pprint import pprint

from popy import local_models_dict, Database, Model, Required, extract_fields, db_session
models_module = import_module(".alternate_fakemodels", "popy")

database = Database(provider="sqlite", filename=":memory:", create_db=True)
models_dict = local_models_dict(models_module)
dbmodels_dict = {}


for model_name, model in models_dict.items():
    fields = extract_fields(model)
    fields["get_fields"] = Model.get_fields
    fields["pydantic_model"] = Model.pydantic_model
    fields["generate_operation"] = Model.generate_operation
    fields["is_popy_model"] = True
    dbmodels_dict[model_name] = type(model_name, (database.Entity, Model), fields)

database.generate_mapping(create_tables=True)
# pprint(dbmodels_dict["ModelA"].__name__)
pprint(dbmodels_dict["ModelA"].pydantic_model("create", models_dict, model_name="ModelA").schema())
# with db_session:
#     x = database.ModelA(arg_a="3")
#     pprint(dir(database.ModelA))
#     pprint(database.ModelA._adict_)
# pprint({ key:value for key, value in models_module.__dict__.items() if isclass(value) and value.__module__ == models_module.__name__})
# pprint(local_models_dict(models_module))