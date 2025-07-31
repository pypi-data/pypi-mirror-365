"""Compatibility module for StrEnum."""
try:
    # Try to import StrEnum from the standard library.
    from enum import StrEnum
except ImportError:
    # Fallback to custom implementation if the import fails.
    from enum import Enum

    class StrEnum(str, Enum):
        """
        A base class for creating enumerations that are also subclasses of `str`.

        `StrEnum` is intended to provide a convenient way to define string constants 
        that are also instances of `Enum`. This can be useful when you need enumerated 
        constants that can be directly compared to strings.

        Note:
            This class is implemented for compatibility with Python versions earlier 
            than 3.11, which do not include the `StrEnum` class in the standard library.
            In Python 3.11 and later, `StrEnum` from the `enum` module  is
            provided by the standard library.
        """

        def __str__(self) -> str:
            """
            Returns the string representation of the enumeration member.

            This method allows an instance of `StrEnum` to be used directly as a string.

            Returns:
                str: The string value of the enumeration member.
            """
            return str(self.value)
