"""Subpackage."""

from typing import TYPE_CHECKING as __tc

if __tc:
    from mastapy._private.scripting._7902 import ApiEnumForAttribute
    from mastapy._private.scripting._7903 import ApiVersion
    from mastapy._private.scripting._7904 import SMTBitmap
    from mastapy._private.scripting._7906 import MastaPropertyAttribute
    from mastapy._private.scripting._7907 import PythonCommand
    from mastapy._private.scripting._7908 import ScriptingCommand
    from mastapy._private.scripting._7909 import ScriptingExecutionCommand
    from mastapy._private.scripting._7910 import ScriptingObjectCommand
    from mastapy._private.scripting._7911 import ApiVersioning
else:
    import sys as __sys

    from lazy_imports import LazyImporter as __LazyImporter

    __import_structure = {
        "_private.scripting._7902": ["ApiEnumForAttribute"],
        "_private.scripting._7903": ["ApiVersion"],
        "_private.scripting._7904": ["SMTBitmap"],
        "_private.scripting._7906": ["MastaPropertyAttribute"],
        "_private.scripting._7907": ["PythonCommand"],
        "_private.scripting._7908": ["ScriptingCommand"],
        "_private.scripting._7909": ["ScriptingExecutionCommand"],
        "_private.scripting._7910": ["ScriptingObjectCommand"],
        "_private.scripting._7911": ["ApiVersioning"],
    }

    __sys.modules[__name__] = __LazyImporter(
        "mastapy",
        globals()["__file__"],
        __import_structure,
    )

__all__ = (
    "ApiEnumForAttribute",
    "ApiVersion",
    "SMTBitmap",
    "MastaPropertyAttribute",
    "PythonCommand",
    "ScriptingCommand",
    "ScriptingExecutionCommand",
    "ScriptingObjectCommand",
    "ApiVersioning",
)
