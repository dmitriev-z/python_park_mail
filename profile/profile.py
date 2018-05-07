import datetime
import inspect
from functools import wraps


def profile(obj):
    if inspect.isfunction(obj):
        result = func_wrapper(obj)
    elif inspect.isclass(obj):
        result = class_wrapper(obj)
    return result


def func_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("`{}` started".format(func.__qualname__))
        start_time = datetime.datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.datetime.now()
        work_time = end_time - start_time
        seconds = work_time.total_seconds()
        print("`{}` finished in {:.5f}s".format(func.__qualname__, seconds))
        return result
    return wrapper


def class_wrapper(cls):
    class_objs = [(name, obj) for name, obj in cls.__dict__.items() if inspect.isfunction(obj)]
    for class_obj in class_objs:
        name, fnc = class_obj
        attr = getattr(cls, name)
        setattr(cls, name, func_wrapper(attr))
    return cls
