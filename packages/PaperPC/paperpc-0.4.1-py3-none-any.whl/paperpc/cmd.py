import sys
import ast
import inspect

from functools import wraps
# Decoration functionality taken from the SO:
# https://stackoverflow.com/questions/3232024/introspection-to-get-decorator-names-on-a-method

# Use the following to retrieve the original names
# of wrapped functions:
# https://stackoverflow.com/questions/4887081/get-the-name-of-a-decorated-function

# Template decorators to characterize
# function signatures

# Bonus: this functionality is now codified in the graffito module:
# https://github.com/dluman/graffito

def generic(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not f.__name__.startswith("__b"):
            args[2]._counter += 1
        else:
            args[2]._spaces[len(args[2]._spaces) - 1] = args[2]._counter + 1
        return f(*args, **kwargs)
    return wrapper

accumulate = generic
value = generic
storage = generic
control_flow = generic
inputs = generic
halt = generic
manipulate = generic

# Create introspection to retrieve
# decorators

def get_signature(cls):
    target = cls
    decorators = {}

    def visit_def(node):
        decorators[node.name] = []
        for n in node.decorator_list:
            name = None
            if isinstance(n, ast.Call):
                name = n.func.attr if isinstance(n.func, ast.Attribute) else n.func.id
            else:
                name = n.attr if isinstance(n, ast.Attribute) else n.id
            decorators[node.name].append(name)

    visitor = ast.NodeVisitor()
    visitor.visit_FunctionDef = visit_def
    visitor.visit(ast.parse(inspect.getsource(target)))
    return decorators

class Commands:

    def __init__(self, show_speed: bool = False):
        self._syntax = {
            "1": {"cmd": self.__add, "cycles": 3},
            "2": {"cmd": self.__sub, "cycles": 3},
            "3": {"cmd":self.__sta, "cycles": 1},
            "4": {"cmd": self.__sft, "cycles": 0},
            "5": {"cmd": self.__lda, "cycles": 2},
            "6": {"cmd": self.__bra, "cycles": 2},
            "7": {"cmd": self.__brz, "cycles": 2},
            "8": {"cmd": self.__brp, "cycles": 2},
            "901": {"cmd": self.__inp, "cycles": 1},
            "902": {"cmd": self.__out, "cycles": 1},
            "903": {"cmd": self.__push, "cycles": 1},
            "904": {"cmd": self.__pop, "cycles": 2},
            "905": {"cmd": self.__ptr, "cycles": 2},
            "906": {"cmd": self.__shi, "cycles": 3},
            "000": {"cmd": self.__hlt, "cycles": 0},
            "0": {"cmd": self.__ptr, "cycles": 2}
        }
        self._show_speed = show_speed
        self._total_clock = 0

    def parse(self, **kwargs):
        try:
            self._line = kwargs['line']
            self._arg = kwargs['arg'][0]
            self._val = int(kwargs['arg'][1:3])
        except KeyError:
            pass
        except:
            print(f"[ERROR] Invalid instruction at line {self._line}.")
        if self._arg == "9":
            self._arg = kwargs['arg']
        try:
            # Carve out specific escape for HALT instruction; the following
            # is always true
            if self._arg == "0" and self._val == 0:
                # The command must be a HALT instruction
                self._arg = "000"
            self._total_clock += self._syntax[self._arg]["cycles"]
            return self._syntax[self._arg]["cmd"]
        except:
            print(f"[ERROR] Invalid instruction at line {self._line}.")
            return

    @accumulate
    def __add(self, acc, storage) -> int:
        add = int(storage._spaces[self._val])
        acc.value += add

    @accumulate
    def __sub(self, acc, storage) -> int:
        sub = int(storage._spaces[self._val])
        acc.value -= sub
        if acc.value < 0:
            acc.value = 0

    @storage
    def __sta(self, acc, storage):
        try:
            storage._spaces[self._val] = str(acc.value)[-3:]
        except IndexError:
            print(f"""
[ERROR] Program attempted to store in {self._val}, but last available
       space is {len(storage._spaces) - 1}.""")
            sys.exit(1)

    @storage
    def __lda(self, acc, storage):
        acc.value = storage._spaces[self._val]

    @storage
    def __bra(self, acc, storage):
        storage._counter = self._val

    @storage
    def __brz(self, acc, storage):
        if acc.value == 0:
            storage._counter = self._val
        else:
            storage._counter += 1

    @storage
    def __brp(self, acc, storage):
        if acc.value > 0:
            storage._counter = self._val
        else:
            storage._counter += 1

    @storage
    def __push(self, acc, storage):
        stack_len = len(storage.stack)
        storage.stack_ptr = storage.stack_base + stack_len
        storage.stack.append(acc.value)
        if storage.stack_ptr - storage.stack_base > storage.stack_size:
            print("[ERROR] Stack overflow!")
            sys.exit(1)
        try:
            storage._spaces[storage.stack_ptr] = acc.value
        except IndexError:
            print(f"[ERROR] Stack pointer set beyond storage limit!")
            sys.exit(1)

    @storage
    def __pop(self, acc, storage):
        stack_len = len(storage.stack)
        stack_pos = storage.stack_base + stack_len
        storage._spaces[storage.stack_ptr] = "---"
        try:
            acc.value = int(storage.stack.pop())
            storage.stack_ptr -= 1
        except IndexError:
            print(f"[ERROR] Stack pointer set beyond storage limit!")
            sys.exit(1)

    @storage
    def __ptr(self, acc, storage):
        acc.value = int(storage.stack_ptr)

    @storage
    def __shi(self, acc, storage):
        acc.value = len(storage.stack)

    @manipulate
    def __sft(self, acc, storage):
        self._val = str(self._val).zfill(2)
        # Left shift first
        if int(self._val[0]) > 0:
            shifts = int(self._val[0])
            tmp = str(acc.value).zfill(4)  + ('0' * shifts)
            acc.value = tmp[-4:]
            if shifts >= 4:
                acc.value = 0
            self._total_clock += shifts
        # Right shift second
        if int(self._val[1]) > 0:
            shifts = int(self._val[1])
            tmp = ('0' * shifts) + str(acc.value).zfill(4)
            acc.value = tmp[0:4]
            if shifts >= 4:
                acc.value = 0
            self._total_clock += shifts
        acc.value = int(acc.value)

    @inputs
    def __inp(self, acc, storage, input: int = 0):
        try:
            int(input)
            if input > 999:
                raise
        except:
            print("Invalid input.")
            sys.exit(1)
        acc.value = input

    def __out(self, acc, storage):
        print(acc.value)
        storage._counter += 1

    @halt
    def __hlt(self, acc, storage):
        if self._show_speed:
            print(f"CYCLES: {self._total_clock}")
        sys.exit(0)
        return False
