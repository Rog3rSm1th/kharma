import re
from kharma.app import ANCHOR_REGEXP, CALL_REGEXP, ELEMENT_REGEXP, LOOP_REGEXP, RANGE_REGEXP, REGEXP_REGEXP
from kharma.app.utils.config import Config
from kharma.app.utils.exceptions import TemplateRecursionError, TemplateStatementError
from kharma.app.utils.numeric import random_int
from kharma.app.utils.objects import KharmaElement
from kharma.app.utils.parser import parse_integer


def handle_anchor(self, string) -> str:
    """
    Replace an anchor reference of the form ++<anchor_name>++ with the anchor value.
    e.g. "++variable++" -> "value_of_my_variable"
    """
    output_string = string

    # Find anchors references
    anchor_statement = re.search(ANCHOR_REGEXP, output_string)

    # Avoid infinite loops caused by circular references
    self.recursion_depth += 1
    if self.recursion_depth > Config.MAX_RECURSION_DEPTH:
        raise TemplateRecursionError("Maximum recursion limit has been exceeded")

    if anchor_statement is None:
        self.recursion_depth = 0
        return output_string

    # Parse anchor name
    anchor_reference = anchor_statement.group(2)

    is_import = anchor_statement.group(1) is not None
    try:
        # ++import:reference++
        if is_import:
            import_reference = anchor_statement.group(1)[:-1]
            import_anchors = self.__class__.imports[import_reference].anchors
            anchor = [anchor for anchor in import_anchors if anchor.name == anchor_reference][0]
            # Handle static variables
            anchor_value = anchor.static_value if anchor.static else anchor.value
        # ++reference++
        else:
            anchor = [anchor for anchor in self.anchors if anchor.name == anchor_reference][0]
            # Handle static variables
            anchor_value = anchor.static_value if anchor.static else anchor.value
    # If reference isn't defined
    except KeyError as e:
        raise ReferenceError("%s is not imported" % import_reference)
    except Exception as e:
        reference_error = "%s:%s" % (import_reference, anchor_reference) if is_import else anchor_reference
        raise ReferenceError("%s is not defined" % reference_error)

    # replace references
    output_string = anchor_value.join(
        [output_string[: anchor_statement.start()], output_string[anchor_statement.end() :]]
    )
    return output_string


def handle_element(self, string: str) -> str:
    """
    Replace an element reference of the form @@<anchor_name>@@ with the element value (element name + counter)
    e.g. "@@element_@@ @@element_@@" -> "element_0 element_1"
    Element counter is incremented at each call to avoid duplicates.
    """
    output_string = string

    # Find elements references
    element_statement = re.search(ELEMENT_REGEXP, output_string)

    if element_statement is None:
        return output_string

    # Parse element name
    element_reference = element_statement.group(1)
    # Element ID
    element_id = element_statement.group(4)

    # Create element if not exists
    element_exists = bool([element for element in self.elements if element.name == element_reference])
    if not element_exists:
        self.elements.append(KharmaElement(element_reference))

    # Generate element value (name + counter)
    element_value = [
        element.value(id_value=element_id) for element in self.elements if element.name == element_reference
    ][0]

    # Replace element reference
    output_string = element_value.join(
        [output_string[: element_statement.start()], output_string[element_statement.end() :]]
    )
    return output_string


def handle_loop(self, string: str) -> str:
    """
    Replace a loop statement of the form [##repeat:<min>:<max>:<dup|nodup>:<separator>##]{%<content>%}
    with a looped string.
    - min: minimum amout of repetitions
    - max: maximum amount of repetitions
    - dup|nodup: allow duplicates if "dup", do not allow if "nodup"
    - separator: string between repetitions
    - content: string to loop
    Content can be an anchor reference (++anchor++) or a element (@@element@@).
    e.g. [##repeat:2:4:nodup:##]{%[a-zA-Z]{5}%} -> fTgyU
    """
    output_string = string

    # Find loop statement
    self.loop_depth += 1
    if self.loop_depth > Config.MAX_LOOP_DEPTH:
        raise RecursionError("Maximum loop recursion limit has been exceeded")

    # Find loop statements
    loop_statement = re.search(LOOP_REGEXP, output_string)

    if loop_statement is None:
        self.loop_depth = 0
        return output_string

    # Parse parameters
    min_repeat = min(int(loop_statement.group(1)), int(loop_statement.group(2)))
    max_repeat = max(int(loop_statement.group(1)), int(loop_statement.group(2)))
    allow_duplicates = loop_statement.group(3) == "dup"
    separator = loop_statement.group(4)

    # Generate looped string array
    loop_array = random_int(min_repeat, max_repeat) * [loop_statement.group(6)]
    # Evaluate all looped strings to find duplicates thereafter
    loop_array = [self.resolve(expression) for expression in loop_array]

    # Remove duplicates if needed
    if not allow_duplicates:
        loop_array_statements = []
        for element in loop_array:
            # Do NOT remove statements/references duplicates
            if any(
                re.compile(regex).match(element)
                for regex in [ELEMENT_REGEXP, ANCHOR_REGEXP, REGEXP_REGEXP, RANGE_REGEXP]
            ):
                loop_array_statements.append(element)

        loop_array = [x for x in loop_array if x not in loop_array_statements]
        loop_array = list(set(loop_array)) + loop_array_statements

    # Loop the string
    loop = separator.join(loop_array)
    output_string = loop.join([output_string[: loop_statement.start()], output_string[loop_statement.end() :]])

    return output_string


def handle_regexp(self, string: str) -> str:
    """
    Replace a regexp statement of the form [%%regexp:<my_regexp>%%] with
    a random valid match for this regular expression.
    e.g. [%%regexp:[a-zA-Z]{5}%%] -> fTgyU
    """
    output_string = string

    # Find regexp statement
    regexp_expression = re.search(REGEXP_REGEXP, output_string)

    if regexp_expression is None:
        return output_string

    # Parse regexp
    regexp = regexp_expression.group(1)

    # Generate a valid regexp input using the regexer
    generated_string = self.regexer.generate_string(regexp)

    # Replace regexp statement with the generated string
    output_string = generated_string.join(
        [output_string[: regexp_expression.start()], output_string[regexp_expression.end() :]]
    )
    return output_string


def handle_range(self, string) -> str:
    """
    Replace a range statement of the form [%%range%%](<min>-<max>) with
    a random integer in this range.
    e.g. [%%range%%](0-100) -> 42
    """
    output_string = string

    # Find range statement
    range_statement = re.search(RANGE_REGEXP, output_string)

    if range_statement is None:
        return output_string

    # Parse parameters
    min_range = parse_integer(range_statement.group(1))
    max_range = parse_integer(range_statement.group(3))
    # Raise an error if min > max
    if min_range > max_range:
        raise TemplateStatementError("Min must be larger than Max value in range statement (%s)" % range_statement)

    # Generate a random integer
    random_integer = str(random_int(min_range, max_range))

    # Replace range statement with the integer
    output_string = random_integer.join(
        [output_string[: range_statement.start()], output_string[range_statement.end() :]]
    )
    return output_string


def handle_call(self, string: str) -> str:
    """
    Replace a call statement of the form [%%call~<function_name>%%](<arg1>, <arg2>, ...)
    with the return value of the function.
    e.g. [%%call~double%%](2) -> 4
    """
    output_string = string

    # Find python statement
    call_statement = re.search(CALL_REGEXP, output_string)

    if call_statement is None:
        return output_string

    # Parse parameters
    is_import = call_statement.group(1) is not None

    function_name = call_statement.group(2)
    arguments = [argument.strip() for argument in call_statement.group(3).split(",")]

    # Resolve the function reference
    try:
        if is_import:
            import_reference = call_statement.group(1)[:-1]
            import_functions = self.__class__.imports[import_reference].functions
            function = [function for function in import_functions if function.name == function_name][0].function
        else:
            function = [function for function in self.functions if function.name == function_name][0].function
    except KeyError as e:
        raise ReferenceError("Function %s:%s is not imported" % (import_reference, function_name))
    except:
        raise ReferenceError("Function %s is not defined" % function_name)

    # Run function with arguments
    function_output = str(function(*arguments))

    # Replace call statement with the function output
    output_string = function_output.join(
        [output_string[: call_statement.start()], output_string[call_statement.end() :]]
    )
    return output_string
