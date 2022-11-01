import copy
import os
import re
from ruamel.yaml import YAML
from typing import List, Tuple
from kharma.app.utils.exceptions import BadTemplateError
from kharma.app.utils.objects import KharmaConst, KharmaElement, KharmaFunction, KharmaObject, KharmaVar
from kharma.app.utils.regexer import Regexer

yaml = YAML()
yaml.preserve_quotes = True  # type: ignore

# [##repeat:<min>:<max>:<dup>:<separator>##]{%%}
LOOP_REGEXP = r"\[##repeat:(?P<minimum>[0-9])+:(?P<maximum>[0-9]+):(?P<dup>dup|nodup):(?P<separator>((?!\[##).)*)##\]\{%((?!\[##).+)%\}"
# [%%regexp:<regexp>%%]
REGEXP_REGEXP = r"\[%%regexp:(?P<content>((?!\[%%).)+)%%\]"
#  ++<anchor>++ OR ++<import>:<anchor>++
ANCHOR_REGEXP = r"\+\+([A-Za-z0-9-_]+:)?(?P<anchor>[A-Za-z0-9-_]+)\+\+"
# @@<element>@@#id=<id>
ELEMENT_REGEXP = r"\@\@(?P<content>((?!\@\@).)+)\@\@(?P<id>#id=([A-Za-z0-9_-]+))?"
# [%%range%%](<min>, <max>)
RANGE_REGEXP = r"\[%%range%%\]\((?P<min>-?([0-9]+|infinity|-infinity)),\s*(?P<max>-?([0-9]+|infinity|-infinity))\)"

# !%python (arg1, arg2, etc...)
#   <python_code>
# %!
PYTHON_REGEXP = r"^(<%python)\s\((([0-9A-Za-z-_]+,? ?)+)\)(\n(.|\n)*)%>$"
# [%%call~function_name%%](<arg1>, <arg2>, ...) OR [%%call~import:function_name%%](<arg1>, <arg2>, ...)
CALL_REGEXP = r"\[%%call~([A-Za-z0-9-_]+:)?(?P<anchor>[A-Za-z0-9-_]+)%%]\(((((?!\[%%)[A-Za-z0-9-_ ])+,? ?)+)\)"


class Kharma:
    """
    Copyright (c) 2022 Rog3rSm1th

    Kharma is a state-of-the-art grammar fuzzer. It can generate many random documents
    based on a grammar which can be used to improve your testing corpus by increasing
    code coverage and to find bugs/vulnerabilities in many kinds of applications
    (interpreters, files parsers, etc...).
    """

    imports: dict = dict()
    imported_paths: list = list()

    from ._handlers import (  # type: ignore
        handle_anchor,
        handle_element,
        handle_loop,
        handle_range,
        handle_regexp,
        handle_call,
    )

    def __init__(self, template_path: str, safe_mode: bool = False) -> None:
        """
        Init Kharma instance.
        """
        # Template path
        self.template_path = os.path.realpath(template_path)

        # Safe mode
        self.safe_mode = safe_mode

        # Template consts
        self.consts: List[KharmaObject] = []
        # Template variables
        self.variables: List[KharmaObject] = []
        # Anchors are consts + variables
        self.anchors: List[KharmaObject] = []
        # Template elements
        self.elements: List[KharmaElement] = []
        # Template functions
        self.functions: List[KharmaFunction] = []

        # Generate valid strings from regex input
        self.regexer = Regexer()

        # init recursion depth
        self.recursion_depth = 0
        # init loop depth
        self.loop_depth = 0

        # Load the template
        self.load()

    def validate_template(self, raw_template: dict) -> None:
        """
        Check if it is a valid Kharma template.
        `
        imports(optional):
            import_name: "import_relative_path.kg"
        consts(optional):
            const1: "value1"
            const2: "value2"
        variables(optional):
            variable1:
                - "possibility1"
                - "possibility2"
        variance(optional):
            main:
                - "++variable1++"
        `
        """
        relative_path = os.path.relpath(self.template_path)

        # Check if template is a dictionary
        if not isinstance(raw_template, dict):
            raise BadTemplateError("Invalid template: %s" % relative_path)

        # Check if all top level sections are valids
        valid_sections_titles = ["imports", "functions", "consts", "variables", "variance"]
        for section_title in raw_template.keys():
            if section_title not in valid_sections_titles:
                raise BadTemplateError("%s is not a valid section in %s" % (section_title, relative_path))

        # Check if all top level sections are (not empty) lists
        for section in raw_template.keys():
            if not isinstance(raw_template[section], dict):
                raise BadTemplateError("%s is not a dictionary in %s" % (section, relative_path))
            if len(raw_template[section]) == 0:
                raise BadTemplateError("%s is empty in %s" % (section, relative_path))

        # Check if variance section has a main var
        if "variance" in raw_template.keys():
            if not "main" in raw_template["variance"].keys():
                raise BadTemplateError("the variance section has no main part in %s" % relative_path)
            # Check if variance.main is a list of strings
            is_list = isinstance(raw_template["variance"]["main"], list)
            is_list_of_strings = all(isinstance(elem, str) for elem in raw_template["variance"]["main"])
            if not is_list_of_strings:
                raise BadTemplateError("main must be a list of strings in %s", relative_path)

        # Check if all functions are strings and respect the function syntax
        if "functions" in raw_template.keys():
            for name in raw_template["functions"]:
                if not isinstance(raw_template["functions"][name], str):
                    raise BadTemplateError("function %s needs to be a string in %s" % (name, relative_path))
                if not re.match(PYTHON_REGEXP, raw_template["functions"][name]):
                    raise BadTemplateError("function %s is invalid in %s" % (name, relative_path))

        # Check if all imports are strings
        if "imports" in raw_template.keys():
            for name in raw_template["imports"]:
                if not isinstance(raw_template["imports"][name], str):
                    raise BadTemplateError(
                        "imports %s needs to be a relative path to another kharma template in %s"
                        % (name, relative_path)
                    )

        # Check if all consts are strings
        if "consts" in raw_template.keys():
            for name in raw_template["consts"]:
                if not isinstance(raw_template["consts"][name], str):
                    raise BadTemplateError("consts %s needs to be a string in %s" % (name, relative_path))

        # Check if all variables are list of strings
        if "variables" in raw_template.keys():
            for name in raw_template["variables"]:
                is_list = isinstance(raw_template["variables"][name], list)
                is_list_of_strings = all(isinstance(elem, str) for elem in raw_template["variables"][name])
                if not is_list and is_list_of_strings:
                    raise BadTemplateError("variable %s needs to be a list of strings in %s" % (name, relative_path))

    def parse_function(self, raw_function: str) -> Tuple:
        """
        Parse a function statement
        Return arguments and content
        """
        function_groups = re.search(PYTHON_REGEXP, raw_function)
        arguments = [argument.strip() for argument in function_groups.group(2).split(",")]  # type: ignore
        content = function_groups.group(4).replace("\n", "\n" + " " * 4)  # type: ignore

        return (arguments, content)

    def parse_template(self, raw_template: dict) -> None:
        """
        Parse a template dict and load constants/variables
        """
        template = copy.deepcopy(raw_template)

        # Parse imports
        if "imports" in raw_template.keys():
            for variable, value in template["imports"].items():
                import_path = os.path.join(os.path.dirname(self.template_path), value)

                if import_path in Kharma.imported_paths:
                    raise BadTemplateError("%s already imported" % import_path)
                Kharma.imported_paths.append(import_path)
                Kharma.imports[variable] = Kharma(import_path, safe_mode=self.safe_mode)

        # Parse functions
        if "functions" in raw_template.keys():
            for variable, value in template["functions"].items():
                parsed_function = self.parse_function(value)
                self.functions.append(KharmaFunction(variable, parsed_function[0], parsed_function[1]))

        # Parse constants
        if "consts" in raw_template.keys():
            for constant, value in template["consts"].items():
                # Static constants
                static = False
                if constant.startswith("static_"):
                    static = True
                self.consts.append(KharmaConst(constant, value, static=static))

        # Parse variables
        if "variables" in raw_template.keys():
            for variable, values in template["variables"].items():
                already_defined = len([const for const in self.consts if const.name == variable]) != 0
                if already_defined:
                    raise BadTemplateError("%s is already defined as a constant" % variable)
                # Static variables
                static = False
                if variable.startswith("static_"):
                    static = True
                self.variables.append(KharmaVar(variable, values, static=static))

        # Parse variance section
        if "variance" in raw_template.keys():
            self.main = KharmaVar("main", template["variance"]["main"])
        # Load anchors
        self.anchors = self.consts + self.variables

    def load(self) -> bool:
        """
        Load a template from a Kharma template (YAML) file.
        """
        try:
            with open(self.template_path, "r") as f:
                template = f.read()
        except:
            raise ValueError("%s is not a valid file path" % self.template_path)

        # Load consts and variables from the template
        loaded_template = yaml.load(template)
        self.validate_template(loaded_template)
        self.parse_template(loaded_template)
        return True

    def evaluate_expression(self, string: str) -> str:
        """
        Evaluate an expression by interpreting statements and references.
        """
        handlers = [
            self.handle_loop,
            self.handle_anchor,
            self.handle_range,
            self.handle_regexp,
            self.handle_element,
            self.handle_call,
        ]

        # Disallow call statements inside templates
        if self.safe_mode:
            handlers.remove(self.handle_call)

        evaluated_string = string
        for handler in handlers:
            evaluated_string = handler(string)
            # Start the whole process again if the string is modified
            if string != evaluated_string:
                return evaluated_string
        return evaluated_string

    def resolve(self, variable: KharmaObject) -> str:
        # Initialize elements
        self.elements = []
        while True:
            evaluated_variable = self.evaluate_expression(variable)
            if evaluated_variable != variable:
                variable = evaluated_variable
            else:
                break

        # Reinitialize loop and recursion depths
        self.loop_depth = 0
        self.recursion_depth = 0

        return evaluated_variable

    def resolve_static_anchors(self):
        """
        Resolve static constants and variables values
        """
        for anchor in self.anchors:
            if anchor.static:
                anchor.static_value = self.resolve(anchor.value)

    def generate(self) -> str:
        """
        Generate a document from a template.
        """
        self.resolve_static_anchors()
        if hasattr(self, "main"):
            evaluated_document = self.resolve(self.main.value)
        else:
            evaluated_document = ""
        return evaluated_document
