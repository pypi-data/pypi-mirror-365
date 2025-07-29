import os
from importlib.metadata import version, PackageNotFoundError
from .core import *

# Attempt to get the version from the package metadata
# If the package is not installed, default to "1.0.0-dev"
try:
    __version__ = version("desu")
except PackageNotFoundError:
    __version__ = "1.0.0-dev"

def help(obj=None):
    """
    Displays the desu package documentation.
    
    If called without arguments, shows the package docstring.
    If called with a function or module, shows its docstring.

    Examples:
        desu.help()               # Shows package docstring
        desu.help(extract)   # Shows docstring of extract function
        desu.help(info)      # Shows docstring of info module
    """
    if obj is None:
        print(__doc__)
    else:
        doc = getattr(obj, '__doc__', None)
        if doc:
            print(doc)
        else:
            print(f"No docstring found for {obj}")


__all__ = [
    "timer",
    "install_packages",
    "import_packages",
    "extract",
    "info",
    "clean",
    "unique_values",
    "unique_count_top_10",
    "unique_count_single_column",
    "unique_count_sorted",
    "fill_with_mean",
    "univariate",
    "bivariate",
    "multivariate"
]

