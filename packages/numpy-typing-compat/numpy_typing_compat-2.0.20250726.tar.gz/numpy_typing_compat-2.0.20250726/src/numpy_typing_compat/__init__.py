from typing import TYPE_CHECKING, Final, Literal

from numpy import long, ulong

if TYPE_CHECKING:
    from typing_extensions import TypeAlias, Never

    import numpy as array_api
    from numpy import dtype

    # there were no `numpy.dtypes.StringDType` typing stubs before numpy 2.1, but
    # because it has no scalar type we use `Never` to indicate its absence.
    StringDType: TypeAlias = dtype[Never]


__all__ = (
    "NUMPY_GE_1_22",
    "NUMPY_GE_1_23",
    "NUMPY_GE_1_25",
    "NUMPY_GE_2_0",
    "NUMPY_GE_2_1",
    "NUMPY_GE_2_2",
    "NUMPY_GE_2_3",
    "StringDType",
    "array_api",
    "long",
    "ulong",
)


def __dir__() -> tuple[str, ...]:
    return __all__


def __getattr__(name: str, /) -> object:
    if name == "array_api":
        import numpy

        return numpy

    if name == "StringDType":
        from numpy.dtypes import StringDType

        return StringDType

    if name in globals():
        return globals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


NUMPY_GE_1_22: Final[Literal[True]] = True  # numpy >= 1.22
NUMPY_GE_1_23: Final[Literal[True]] = True  # numpy >= 1.23
NUMPY_GE_1_25: Final[Literal[True]] = True  # numpy >= 1.25
NUMPY_GE_2_0: Final[Literal[True]] = True  # numpy >= 2.0
NUMPY_GE_2_1: Final[Literal[False]] = False  # numpy >= 2.1
NUMPY_GE_2_2: Final[Literal[False]] = False  # numpy >= 2.2
NUMPY_GE_2_3: Final[Literal[False]] = False  # numpy >= 2.3
