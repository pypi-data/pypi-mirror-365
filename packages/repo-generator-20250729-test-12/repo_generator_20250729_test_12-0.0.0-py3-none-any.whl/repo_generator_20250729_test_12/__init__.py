"""repo_generator_20250729_test_12 package."""

# Re-export main functionality
from .states_info import is_city_capitol_of_state, slow_add

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("repo_generator_20250729_test_12")
except PackageNotFoundError:
    # Package not installed, fallback to development version
    __version__ = "dev"

__all__ = ["__version__", "is_city_capitol_of_state", "slow_add"]
