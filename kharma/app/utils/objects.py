import random
import types
from typing import List


class KharmaObject:
    """
    Base object from which all Kharma objects are derived
    """

    pass


class KharmaConst(KharmaObject):
    """
    A constant has a name and an unique string value
    Can be called with ++<const_name>++
    """

    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value


class KharmaVar(KharmaObject):
    """
    A variable has a name and a list of possible strings values
    Can be called with ++<variable_name>++
    """

    def __init__(self, name: str, values: List[str]) -> None:
        self.name = name
        self.values = [value for value in values]

    @property
    def value(self) -> str:
        """
        Select a random value among the options
        """
        return random.choice(self.values)


class KharmaElement(KharmaObject):
    """
    An element has a name and a counter
    Can be called with @@<element_name>@@
    """

    def __init__(self, name: str):
        self.name = name
        self.counter = 0

    @property
    def value(self):
        """
        Concatenation of value and counter.
        """
        value = "%s%s" % (self.name, str(self.counter))
        self.counter += 1
        return value


class KharmaFunction(KharmaObject):
    """
    A function has a name, and a list of arguments
    Can be called with [%%call~function_name%%](arg1, arg2)
    """

    def __init__(self, name: str, arguments: List[str], content: str) -> None:
        self.name = name
        self.arguments = arguments
        self.content = "def %s(%s): %s" % (self.name, ", ".join(arguments), content)

        compiled_content = compile(self.content, "<string>", "exec")
        self.function = types.FunctionType(compiled_content.co_consts[0], globals())

    def value(self, user_input: List[str]):
        """
        Get the return value of the called function
        """
        self.function(*user_input)
