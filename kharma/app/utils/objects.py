import random
import types
from typing import List, Tuple


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

    def __init__(self, name: str, value: str, static: bool = False) -> None:
        self.name = name
        self.value = value
        # Static consts
        self.static = static
        self.static_value = None


class KharmaVar(KharmaObject):
    """
    A variable has a name and a list of possible strings values
    Can be called with ++<variable_name>++
    """

    def __init__(self, name: str, values: List[str], static: bool = False) -> None:
        self.name = name
        self.values = [value for value in values]
        # Static variables
        self.static = static
        self.static_value = None

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
        self.ids: List[Tuple] = []

    def value(self, id_value: str = None) -> str:
        """
        Concatenation of value and counter.
        """
        # Use of an ID
        if id_value is not None:
            id_value_list = list(filter(lambda id_tuple: id_tuple[0] == id_value, self.ids))
            # If first occurrence of the ID
            if len(id_value_list) == 0:
                counter = self.counter
                self.ids.append((id_value, self.counter))
                self.counter += 1
            # If existing ID
            else:
                counter = id_value_list[0][1]
        # No ID
        else:
            counter = self.counter
            self.counter += 1
        # Compute value
        value = "%s%s" % (self.name, str(counter))
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
