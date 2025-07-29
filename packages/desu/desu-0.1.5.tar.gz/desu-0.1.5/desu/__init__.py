import os
from importlib.metadata import version, PackageNotFoundError
from .core import *

# Attempt to get the version from the package metadata
# If the package is not installed, default to "1.0.0-dev"
try:
    __version__ = version("desu")
except PackageNotFoundError:
    __version__ = "1.0.0-dev"

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

