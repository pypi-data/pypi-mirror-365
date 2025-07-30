<h1 align="center">
<img src="https://documentation.smartmt.com/MastaAPI/15.0/images/smt_logo.png" width="150" alt="SMT"><br>
<img src="https://documentation.smartmt.com/MastaAPI/15.0/images/MASTA_15_logo.png" width="400" alt="Mastapy">
</h1><br>

[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python](https://img.shields.io/pypi/pyversions/mastapy
)

Mastapy is the Python scripting API for MASTA.

- **Website**: https://www.smartmt.com/
- **Support**: https://support.smartmt.com/
- **Documentation**: https://documentation.smartmt.com/MastaAPI/15.0/


### Features

- Powerful integration with MASTA with the ability to run Python scripts from the MASTA interface directly.
- Ability to use MASTA functionality external to the MASTA software in an independent script.
- An up-to-date and tight integration with Python. This is not a lightweight wrapper around the C# API. It is specifically designed for Python and works great in tandem with other common scientific Python packages (e.g. SciPy, NumPy, Pandas, Matplotlib, Seaborn, etc.)
- Extensive backwards compatibility support. Scripts written in older versions of mastapy will still work with new versions of MASTA.
- Full support for Linux and .NET 8.0 versions of the MASTA API.

### Release Information

#### Major Changes

- Importing local modules and packages is now fully supported by scripted properties.
- This package is now built using UV.
- Adds support for .NET 8.0 versions of the MASTA API.

#### Minor Changes

- Improved handling of invalidated (and read-only) properties.
- Improved exception handling. More exceptions are now exposed to users through the `mastapy.exceptions` module.
- Failed analyses are now reported to a user via an exception.
- Various improvements and bug fixes.

### Importing Local Modules or Packages in Scripted Properties

Previously, the expectation was scripted property code was contained within a single file. However, this could become unwieldy as the functionality of the scripted property grew. Refactoring code into separate modules and packages would be a natural progression and has always been supported, but any subsequent updates to that external code was not properly loaded into MASTA.

This update adds full support for that scenario. For example, take the following Python script, `scripted_property.py`, which contains a single scripted property. Note how it imports two separate modules from `my_package`.

```python
"""scripted_property.py"""

from mastapy import masta_property
from mastapy.system_model.part_model import RootAssembly

# Importing modules from a local package called "my_package"
from my_package import a
from my_package.sub_package import b


@masta_property("my_property")
def my_property(root_assembly: RootAssembly) -> None:
    ...
```

The following is the scripted properties directory in this scenario. `my_package` is defined right next to our `scripted_property.py` file, making it a locally imported package.

```
my_scripts/
├─ my_package/
│  ├─ sub_package/
│  │  ├─ b.py
│  │  ├─ __init__.py
│  ├─ __init__.py
│  ├─ a.py
├─ scripted_property.py
```

With this new update, any changes made to the files within `my_package` are detected by MASTA, without having to refresh the scripts. This makes it possible to share code between scripted properties in separate files and develop a more professional and reusable codebase.

### Improved Handling of Invalidated (and Read-Only) Properties

It is now easier to work with invalidated properties in your design. Several ways of handling them have been added.

The first option is to simply catch the exception:

```python
from mastapy.exceptions import InvalidatedPropertyException

try:
    value = design.material_agma
except InvalidatedPropertyException:
    # Do something
    ...
```

Or suppress it:

```python
import contextlib
from mastapy.exceptions import InvalidatedPropertyException

with contextlib.suppress(InvalidatedPropertyException):
    value = design.material_agma
```

Alternatively, you can check if a property is valid before accessing it by using `is_valid`. This method now accepts Pythonic snake_case names. `is_read_only` has been similarly updated.

```python
if design.is_valid("material_agma"):
    ...
```

Or use the `get_property` and `set_property` methods. In particular, `get_property` will return `None` if the property is invalidated, which makes it convenient to use with the walrus operator:

```python
if (value := design.get_property("material_agma")) is not None:
    ...
```
