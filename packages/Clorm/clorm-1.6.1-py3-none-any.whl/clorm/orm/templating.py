"""Predicate sub-class function templates.

Some of the functions of a Predicate sub-class are generated dynamically using
an `exec()` call. This file contains some template code snippets and functions
to help apply these templates.

"""

from __future__ import annotations

# ------------------------------------------------------------------------------
# Helper functions for PredicateMeta class to create a Predicate
# class constructor.
# ------------------------------------------------------------------------------


def expand_template(template: str, **kwargs: str) -> str:
    """Expand the template by substituting the arguments.

    If the argument contains multiple lines then extra spaces are added to each
    line to preserve the correct indentation.

    """

    # Add spaces to each line of some multi-text input
    def add_spaces(num, text):
        space = " " * num
        out = []
        for idx, line in enumerate(text.splitlines()):
            if idx == 0:
                out = [line]
            else:
                out.append(space + line)
        return "\n".join(out)

    if not template:
        return ""
    lines = template.expandtabs(4).splitlines()
    outlines = []
    for line in lines:
        start = line.find(r"{%")
        if start == -1:
            outlines.append(line)
            continue
        end = line.find(r"%}", start)
        if end == -1:
            raise ValueError("Bad template expansion in {line}")
        keyword = line[start + 2 : end]
        text = add_spaces(start, kwargs[keyword])
        line = line[0:start] + text + line[end + 2 :]
        outlines.append(line)
    return "\n".join(outlines)


PREDICATE_TEMPLATE = r"""
def __init__(self,
             {{%args_signature%}}
             *, sign: bool=True) -> None:

    self._hash = None
    self._sign = bool(sign)

    {{%sign_check%}}
    {{%check_no_defaults%}}

    # Assign defaults for missing values and apply map tuple transform for complex values
    {{%assign_defaults%}}
    {{%check_complex%}}

    self._field_values = ({{%args%}})

    # Create the raw symbol
    self._raw = Function("{pdefn.name}",
                         ({{%args_raw%}}),
                         self._sign)


@classmethod
def _unify(cls: Type[_P], raw: AnySymbol, raw_args: Optional[Sequence[AnySymbol]]=None, raw_name: Optional[str]=None) -> Optional[_P]:
    try:
        raw_args = raw_args if raw_args else raw.arguments
        raw_name = raw_name if raw_name else raw.name
        if len(raw_args) != {pdefn.arity}:
            return None

        {{%sign_check_unify%}}

        if raw_name != "{pdefn.name}":
            return None

        instance = cls.__new__(cls)
        instance._raw = raw
        instance._hash = None
        instance._sign = raw.positive
        instance._field_values = ({{%args_cltopy%}})
        return instance
    except (TypeError, ValueError):
        return None
    except AttributeError as e:
        raise ValueError((f"Cannot unify with object {{raw}} ({{type(raw)}}) as "
                          "it is not a clingo Symbol Function object"))


def nontuple__eq__(self, other: Any) -> bool:
    # Deal with a non-tuple predicate
    if isinstance(other, Predicate):
        return self._raw == other._raw
    if isinstance(other, Symbol):
        return self._raw == other
    return NotImplemented


def tuple__eq__(self, other: Any) -> bool:
    # Deal with a predicate that is a tuple
    if isinstance(other, Predicate):
        return self._raw == other._raw
    if isinstance(other, Symbol):
        return self._raw == other
#    if isinstance(other, tuple):
#        return self._field_values == other
    return NotImplemented


def nontuple__lt__(self, other):
    # If it is the same predicate class then compare the underlying clingo symbol
    if isinstance(other, Predicate):
        return self._raw < other._raw
    if isinstance(other, Symbol):
        return self._raw < other
    return NotImplemented


def tuple__lt__(self, other):
    # self is always less than a non-tuple predicate
    if isinstance(other, Predicate):
        return self._raw < other._raw
    if isinstance(other, Symbol):
        return self._raw < other
#    if isinstance(other, tuple):
#        return self._field_values < other
    return NotImplemented


def nontuple__gt__(self, other):
    if isinstance(other, Predicate):
        return self._raw > other._raw
    if isinstance(other, Symbol):
        return self._raw > other
    return NotImplemented


def tuple__gt__(self, other):
    # If it is the same predicate class then compare the sign and fields
    if isinstance(other, Predicate):
        return self._raw > other._raw
    if isinstance(other, Symbol):
        return self._raw > other
#    if isinstance(other, tuple):
#        return self._field_values > other
    return NotImplemented


def __ge__(self, other):
    result = self.__lt__(other)
    if result is NotImplemented:
        return NotImplemented
    return not result


def __le__(self, other):
    result = self.__gt__(other)
    if result is NotImplemented:
        return NotImplemented
    return not result


def __hash__(self):
    if self._hash is None:
        self._hash = hash(self._raw)
    return self._hash


__eq__ = tuple__eq__ if PREDICATE_IS_TUPLE else nontuple__eq__
__lt__ = tuple__lt__ if PREDICATE_IS_TUPLE else nontuple__lt__
__gt__ = tuple__gt__ if PREDICATE_IS_TUPLE else nontuple__gt__



"""

CHECK_SIGN_TEMPLATE = r"""
# Check if the sign is allowed
if self._sign != {sign}:
    raise ValueError(f"Predicate {{type(self).__name__}}"
                     f"is defined to only allow {pdefn.sign} instances")
"""

CHECK_SIGN_UNIFY_TEMPLATE = r"""
if raw.positive != {sign}:
    return None
"""

NO_DEFAULTS_TEMPLATE = r"""
# Check for missing values that have no defaults
if MISSING in ({args}):
    for arg, name in ({named_args}):
        if arg is MISSING:
            raise TypeError((f"Missing argument for field \"{{name}}\""
                             f"(which has no default value)"))
"""

ASSIGN_DEFAULT_TEMPLATE = r"""
if {arg} is MISSING:
    {arg} = {arg}_field.default
"""

ASSIGN_COMPLEX_TEMPLATE = r"""
if not isinstance({arg}, {arg}_class):
    if isinstance({arg}, tuple) or (isinstance({arg}, Predicate) and {arg}.meta.is_tuple):
        {arg} = {arg}_class(*{arg})
    else:
        raise TypeError(f"Value {{{arg}}} ({{type({arg})}}) is not a tuple")
"""

PREDICATE_UNIFY_DOCSTRING = r"""
    Unify a (raw) Symbol object with the class.

    Returns None on failure to unify otherwise returns the new fact
"""

# ------------------------------------------------------------------------------
# main
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    raise RuntimeError("Cannot run modules")
