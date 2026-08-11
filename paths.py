import sys
from pathlib import Path


def base_dir():
    """Directory the exe (or script) lives in, so config/output stay next to it
    regardless of the current working directory the user launched it from."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent
