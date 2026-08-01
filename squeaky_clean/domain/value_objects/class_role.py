"""ClassRole enum: the polymorphic role a ClassSpec plays in its module."""

from enum import Enum


class ClassRole(Enum):
    """Role derived from a ClassSpec's implements/concretes fields.

    ABSTRACT: declares concretes — emitters render it as an interface.
    CONCRETE: declares an implements target — a polymorphic variant.
    PLAIN: neither — an ordinary standalone class.
    """

    ABSTRACT = "abstract"
    CONCRETE = "concrete"
    PLAIN = "plain"
