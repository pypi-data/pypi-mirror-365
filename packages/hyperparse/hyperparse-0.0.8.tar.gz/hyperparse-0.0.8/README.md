# Hyperparse : A Simple Shell Environment Variables Parser 

## Introduction
This script provides a way to parse environment variables and use them as hyperparameters in Python scripts.

The script parses a string that contains a comma-separated list of key-value pairs, where each key-value pair is separated by an equal sign (=). The keys should be strings, and the values can be integers, floats, lists of integers or floats, booleans, or None. The script can handle values that are enclosed in single or double quotes.

The script also provides a set_hyper function that allows you to set the variables in your Python script. You can pass in a dictionary of hyperparameters and a namespace or dictionary of arguments. The function will update the namespace or dictionary with the hyperparameters.


## Usage

### Directly parsing string
```python
# main.py
from hyperparse import parse_string, reset_hyper
config1 = "a=1,b=hello,c=[1,2,3]"
config2 = "d=4,e=3.2,b=world"  # b will override config1's value
usermode = parse_string(config1)
usermode.update(parse_string(config2))
reset_hyper(usermode)
print(a) # 1
print(b) # world
print(c) # [1, 2, 3]
print(d) # 4
print(e) # 3.2
```

### Parse environment variables
First set a variable in shell and run the python file `main.py`.
```bash
export usermode="a=1,b,c=[1,2,3],d=4,e=3.2,f=itud,g=False"
python main.py
```
```python
# main.py
from hyperparser import get_hyper
usermode = get_hyper("usermode")
print(usermode)
# {"a": 1, "b": None, "c": [1, 2, 3], "d": 4, "e": 3.2, "f": "itud"}
```

### Reset argparse elements

```python
# main.py
from hyperparse import get_hyper, set_hyper
usermode = get_hyper("usermode")
parser = argparse.ArgumentParser()
parser.add_argument('--a', type=int, default=5)
parser.add_argument('--f', type=str, default="hello")
args = parser.parse_args()
set_hyper(usermode, args)
print(args) # Namespace(a=1, f='itud')
```

### Reset Local Variables
```python
# main.py
from hyperparse import get_hyper, set_hyper
usermode = get_hyper("usermode")
a = 5
f = "stk"
set_hyper(usermode)
print(a) # 1
print(f) # itud
```# hyperparse
