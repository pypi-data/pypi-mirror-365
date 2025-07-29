import re
import os
import inspect
import argparse
import ctypes
import sys

global var_list, str_list
var_list = {}
str_list = {}

def convert_float(s):
    try:
        return float(s)
    except:
        return None

def parse_value(value):
    if value.isdigit():
        return int(value)
    elif convert_float(value) is not None:#"." in value and value.replace(".", "", 1).isdigit():
        return float(value)
    elif value.lower() == "none":
        return None
    elif value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    elif value == "":
        return None
    else:
        return value.strip("'\"")


def parse_string(s):
    if type(s) is tuple:
        s = ",".join(s)
    d = {}
    items = re.findall(r'([^=,]+(?:\[[^\]]*\])?)=?(\[[^\]]*\]|[^,]*)', s)
    for key, value in items:
        if value.startswith("[") and value.endswith("]"):
            value = value[1:-1].split(",")
            value = [parse_value(v) for v in value]
        else:
            value = parse_value(value)
        d[key] = value
    return d

#s = "a=1,b,c=[1,2,3],d=4,e=3.2,f=itud,g=False"
def parse_env(name):
    env_vars = os.environ
    value = env_vars[name]
    result = parse_string(value)
    var_list[name] = result
    str_list[name] = value

"""for key, value in env_vars.items():
    result = parse_string(value)
    if key not in globals():
        globals()[key] = result
        globals()[key + "_str"] = value"""


def parse(name = ""):
    mode = {}
    if name not in var_list:
        if type(name) is str and name in os.environ:
            parse_env(name)
        elif f"--{name}" in sys.argv:
            parse_arg(name)
        elif len(sys.argv) > 1:
            parse_arg(name)
        else:
            var_list[name] = {}
    mode = var_list[name]

    if name not in str_list:
        mode_str = ""
    else:
        mode_str = str_list[name]
    return mode, mode_str

def get_hyper_str(name):
    if name not in str_list:
        parse(name)
    if name not in str_list:
        return None
    else:
        return str_list[name]

def parse_arg(name):
    if type(name) is int:
        try:
            value = sys.argv[name]
        except IndexError:
            print(f"You do not have {name} arguments")
            value = ""
    elif name != "":
        parser = argparse.ArgumentParser()
        parser.add_argument(f"--{name}", type=str, default="")
        args, unknown_args = parser.parse_known_args()
        value = getattr(args, name)
        sys.argv = [sys.argv[0]] + unknown_args
    else:
        value = sys.argv[1]
    result = parse_string(value)
    var_list[name] = result
    str_list[name] = value
    

def reset_hyper(hyper, pargs=None):
    if type(hyper) is str:
        hyper = parse(hyper)[0]
    if pargs is None:
        frame = inspect.currentframe().f_back
        pargs = frame.f_locals
    for k in hyper:
        v = hyper[k]
        if type(pargs) is dict:
            pargs[k] = v
        elif hasattr(pargs, '__setitem__'):
            # Python 3.13+ returns FrameLocalsProxy which supports item assignment
            pargs[k] = v
        else:
            setattr(pargs, k, v)
    if 'frame' in locals() and sys.version_info < (3, 13):
        ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))
    

