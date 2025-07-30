from .data.core import *
from .data.function import *
from .update import HProcessUpdateWarning, check, _getVersion

check()

__version__ = _getVersion()
__title__ = "hprocess"