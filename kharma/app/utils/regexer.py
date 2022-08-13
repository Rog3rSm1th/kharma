import itertools
import string
import sys
from random import choice

try:
    from re import _parser  # type: ignore
except ImportError:
    import sre_parse as _parser  # type: ignore
from typing import Any, Pattern, Tuple
from kharma.app.utils.numeric import random_int


class Regexer:
    """
    The regexer allows to generate a random valid match for a given regexp
    Usage: Regexer().generate_string(r"myregexp")
    """

    def __init__(self):
        # Max allowed amount of repetitions
        self.limit = 30
        # Cache
        self.cache = dict()

        # Alphabets tokens
        self.alphabets = {
            "printable": string.printable,
            "letters": string.ascii_letters,
            "uppercase": string.ascii_uppercase,
            "lowercase": string.ascii_lowercase,
            "digits": string.digits,
            "punctuation": string.punctuation,
            "nondigits": string.ascii_letters + string.punctuation,
            "nonletters": string.digits + string.punctuation,
            "whitespace": string.whitespace,
            "nonwhitespace": string.printable.strip(),
            "normal": string.ascii_letters + string.digits + " ",
            "word": string.ascii_letters + string.digits + "_",
            "nonword": "".join(set(string.printable).difference(string.ascii_letters + string.digits + "_")),
            "postalsafe": string.ascii_letters + string.digits + " .-#/",
            "urlsafe": string.ascii_letters + string.digits + "-._~",
            "domainsafe": string.ascii_letters + string.digits + "-",
        }

        # Categories tokens
        self.categories = {
            "category_digit": lambda: self.alphabets["digits"],
            "category_not_digit": lambda: self.alphabets["nondigits"],
            "category_space": lambda: self.alphabets["whitespace"],
            "category_not_space": lambda: self.alphabets["nonwhitespace"],
            "category_word": lambda: self.alphabets["word"],
            "category_not_word": lambda: self.alphabets["nonword"],
        }

        # Cases tokens
        self.cases = {
            "literal": lambda x: chr(x),
            "not_literal": lambda x: choice(string.printable.replace(chr(x), "")),
            "at": lambda x: "",
            "in": lambda x: self.handle_in(x),
            "any": lambda x: choice(string.printable.replace("\n", "")),
            "range": lambda x: [chr(i) for i in range(x[0], x[1] + 1)],
            "category": lambda x: self.categories[str(x).lower()](),
            "branch": lambda x: "".join(self.handle_state(i) for i in choice(x[1])),
            "subpattern": lambda x: self.handle_group(x),
            "assert": lambda x: "".join(self.handle_state(i) for i in x[1]),
            "assert_not": lambda x: "",
            "groupref": lambda x: self.cache[x],
            "min_repeat": lambda x: self.handle_repeat(*x),
            "max_repeat": lambda x: self.handle_repeat(*x),
            "negate": lambda x: [False],
        }

    def parse_regexp(self, regexp: Pattern[str]) -> list[Any]:
        """
        Parse a regex using re._parse.parse
        Return a list of states
        """
        parsed_regexp = _parser.parse(regexp)
        return parsed_regexp

    def handle_state(self, state: Tuple[Any]) -> str:
        """
        Generate a string from a given state.
        """
        opcode, value = state  # type: ignore
        handled_state = self.cases[str(opcode).lower()](value)  # type: ignore
        return handled_state

    def handle_in(self, value: list) -> str:
        """
        Handle IN token.
        """
        states_values = [self.handle_state(i) for i in value]
        candidates = list(itertools.chain(*states_values))
        # [^] pattern
        if candidates[0] is False:
            candidates = set(string.printable).difference(candidates[1:])
        # Choose a random value between candidates
        return choice(candidates)

    def handle_group(self, value: list) -> str:
        """
        Handle GROUP token.
        """
        # Handle python versions below 3.6
        if sys.version_info < (3, 6):
            result = "".join(self.handle_state(i) for i in value[1])
        else:
            result = "".join(self.handle_state(i) for i in value[3])
        if value[0]:
            self.cache[value[0]] = result
        return result

    def handle_repeat(self, start_range: int, end_range: int, value: Any) -> str:
        """
        Handle REPEAT token.
        """
        result: list[Any] = []
        end_range = min(end_range, self.limit)

        # Repeat a pattern a random number of times
        times = random_int(start_range, max(start_range, end_range))

        for i in range(times):
            occurence = "".join(self.handle_state(i) for i in value)
            result.append(occurence)
        return "".join(result)

    def build_string(self, parsed_regex: list[Any]) -> str:
        """
        Build a string given a list of regular expression tokens.
        """
        output_string = []
        for state in parsed_regex:
            handled_state = self.handle_state(state)
            output_string.append(handled_state)
        return "".join(output_string)

    def generate_string(self, regexp: Pattern[str]) -> str:
        """
        Generate a valid input matching a regular expression.
        """
        parsed_regexp = self.parse_regexp(regexp)
        output_string = self.build_string(parsed_regexp)
        return output_string
