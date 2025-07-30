from .data.core import *
from .data.function import *
from .update import _getVersion

_AUTO_CHECK = False


def update(enable: bool = True):
    """启用/禁用导入时的自动更新检查"""
    global _AUTO_CHECK
    _AUTO_CHECK = enable

# 只在启用自动检查时执行
if _AUTO_CHECK:
    from .update import HProcessUpdateWarning, check
    check()
    del check  # 避免在模块中暴露check函数，保持接口清晰

__version__ = _getVersion()
