class BadTemplateError(Exception):
    """
    Raised if a template is invalid
    """

    pass


class TemplateRecursionError(Exception):
    """
    Raised if we exceeded the max allowed amount of recursion
    """

    pass


class ReferenceError(Exception):
    """
    Raised if a non-existing anchor is referenced
    """

    pass


class TemplateStatementError(Exception):
    """
    Raised when an invalid statement is used inside a template
    """

    pass
