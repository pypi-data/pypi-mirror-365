"""sample_generated_20250730_01_repo package."""

# Re-export main functionality
from .states_info import is_city_capitol_of_state, slow_add

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    # Python < 3.8 fallback
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("sample_generated_20250730_01_repo")
except PackageNotFoundError:
    # Package not installed, fallback to development version
    __version__ = "dev"

__all__ = ["__version__", "is_city_capitol_of_state", "slow_add"]
