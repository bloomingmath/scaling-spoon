from ponydb import db
from ponydb import db_session
from inspect import signature
import functools
import forge



def f():
    return "and that's it."

def kwarg_wrap(func, kw, kwh='str', kwd=''):
    d = {'func': func, 'kw': kw, 'functools': functools, 'signature':signature, 'forge':forge}
    exec("""
print(forge.fsignature(func))

@forge.sign(
    forge.arg('{kw}'),
    *forge.fsignature(func)
)
def wfunc({kw}='undefined', **kwargs):
    return "{kw} is %i... " % {kw} + func(**kwargs)
    """.format(kw=kw), d)
    return d["wfunc"]

def async_kwarg_wrap(func, kw):
    d = {'func': func, 'kw': kw}
    exec("""async def wfunc({kw}='undefined', **kwargs):
        return "{kw} is %i... " % {kw} + await func(**kwargs)""".format(kw=kw), d)
    return d["wfunc"]

f1 = kwarg_wrap(f, 'a')
f2 = kwarg_wrap(f1, 'b')
f3 = kwarg_wrap(f2, 'c')

async def af():
    print("Async: No arguments")

