def _getVersion() -> str:
    """获取hprocess模块版本"""
    from .data.version import __version__
    return __version__

import re
import warnings
import json
from urllib.request import urlopen
from urllib.error import URLError
from typing import Optional, Callable

# 自定义警告类，继承自UserWarning
class HProcessUpdateWarning(UserWarning):
    """警告用户有可用的hprocess模块更新"""
    pass

def getVersion() -> str:
    return _getVersion()

class UpdateChecker:
    def __init__(self, package_name: str = "hprocess"):
        """
        初始化更新检查器
        
        :param package_name: PyPI上的包名称
        """
        self.package_name = package_name
        self.current_version = getVersion()  # 使用当前文件的getVersion方法
    
    @staticmethod
    def _version_to_tuple(version_str: str) -> tuple:
        """
        将版本字符串转换为可比较的整数元组
        
        :param version_str: 版本号字符串 (格式: "x.y.z")
        :return: 整数元组 (x, y, z)
        """
        # 提取数字部分并转换为整数
        parts = []
        for part in re.findall(r'\d+', version_str):
            parts.append(int(part))
            if len(parts) >= 3:
                break
        
        # 确保至少有3个部分 (不足补0)
        while len(parts) < 3:
            parts.append(0)
            
        return tuple(parts[:3])
    
    def is_outdated(self, current: str, latest: str) -> bool:
        """
        检查当前版本是否低于最新版本
        
        :param current: 当前版本号
        :param latest: 最新版本号
        :return: 是否需要更新
        """
        return self._version_to_tuple(current) < self._version_to_tuple(latest)
    
    def get_latest_version_from_pypi(self) -> Optional[str]:
        """
        从PyPI获取最新版本号
        
        :return: 最新版本号字符串，如果获取失败则返回None
        """
        url = f"https://pypi.org/pypi/{self.package_name}/json"
        try:
            with urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data['info']['version']
        except (URLError, KeyError, json.JSONDecodeError, TimeoutError) as e:
            warnings.warn(f"从PyPI获取最新版本失败: {str(e)}", RuntimeWarning)
            return None

def check():
    """
    检查更新并发出HProcessUpdateWarning（外部调用方法）
    """
    checker = UpdateChecker()
    latest_version = checker.get_latest_version_from_pypi()
    
    if latest_version and checker.is_outdated(checker.current_version, latest_version):
        msg = (
            f"Discover new version: {latest_version} (currently used: {checker.current_version})n"
            f"Please update with 'pip install --upgrade {checker.package_name}'"
        )
        # 使用自定义的HProcessUpdateWarning发出警告
        warnings.warn(msg, HProcessUpdateWarning)