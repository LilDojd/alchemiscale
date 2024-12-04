from alchemiscale import ScopedKey
from typing import List, Optional
from .encoding import CypherEncoder
from ._types import string_types


def cypher_list_from_scoped_keys(scoped_keys: List[Optional[ScopedKey]]) -> str:
    """Generate a Cypher list structure from a list of ScopedKeys, ignoring NoneType entries.

    Parameters
    ----------
    scoped_keys
        List of ScopedKeys to generate the Cypher list

    Returns
    -------
    str
        Cypher list
    """

    if not isinstance(scoped_keys, list):
        raise ValueError("`scoped_keys` must be a list of ScopedKeys")

    data = []
    for scoped_key in scoped_keys:
        if scoped_key:
            data.append('"' + str(scoped_key) + '"')
    return "[" + ", ".join(data) + "]"


def cypher_or(items):
    return "|".join(items)


# Original code from py2neo, licensed under the Apache License 2.0.
def cypher_join(*clauses, **parameters):
    """Join multiple Cypher clauses, returning a (query, parameters)
    tuple. Each clause may either be a simple string query or a
    (query, parameters) tuple. Additional `parameters` may also be
    supplied as keyword arguments.

    :param clauses:
    :param parameters:
    :return: (query, parameters) tuple
    """
    query = []
    params = {}
    for clause in clauses:
        if clause is None:
            continue
        if isinstance(clause, tuple):
            try:
                q, p = clause
            except ValueError:
                raise ValueError(
                    "Expected query or (query, parameters) tuple "
                    "for clause %r" % clause
                )
        else:
            q = clause
            p = None
        query.append(q)
        if p:
            params.update(p)
    params.update(parameters)
    return "\n".join(query), params


# Original code from py2neo, licensed under the Apache License 2.0.
class CypherExpression(object):
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value


# Original code from py2neo, licensed under the Apache License 2.0.
def cypher_escape(identifier):
    """Return a Cypher identifier, with escaping if required.

    Simple Cypher identifiers, which just contain alphanumerics
    and underscores, can be represented as-is in expressions.
    Any which contain more esoteric characters, such as spaces
    or punctuation, must be escaped in backticks. Backticks
    themselves are escaped by doubling.

    ::

        >>> cypher_escape("simple_identifier")
        'simple_identifier'
        >>> cypher_escape("identifier with spaces")
        '`identifier with spaces`'
        >>> cypher_escape("identifier with `backticks`")
        '`identifier with ``backticks```'

    Identifiers are used in Cypher to denote named values, labels,
    relationship types and property keys. This function will typically
    be used to construct dynamic Cypher queries in places where
    parameters cannot be used.

        >>> "MATCH (a:{label}) RETURN id(a)".format(label=cypher_escape("Employee of the Month"))
        'MATCH (a:`Employee of the Month`) RETURN id(a)'

    :param identifier: any non-empty string
    """
    if not isinstance(identifier, string_types):
        raise TypeError(type(identifier).__name__)
    encoder = CypherEncoder()
    return encoder.encode_key(identifier)


# Original code from py2neo, licensed under the Apache License 2.0.
def cypher_repr(value, **kwargs):
    """Return the Cypher representation of a value.

    This function attempts to convert the supplied value into a Cypher
    literal form, as used in expressions.

    """
    encoder = CypherEncoder(**kwargs)
    return encoder.encode_value(value)
