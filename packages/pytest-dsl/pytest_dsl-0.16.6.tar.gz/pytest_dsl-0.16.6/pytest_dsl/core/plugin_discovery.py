"""插件发现模块

该模块提供了下列功能：
1. 使用entry_points机制发现和加载第三方关键字插件
2. 扫描本地内置关键字（向后兼容）
3. 自动扫描并导入用户项目中的keywords目录下的关键字模块

自定义关键字目录结构：
- 项目根目录/
  - keywords/                  # 关键字根目录
    - __init__.py              # 可选，如果要作为包导入
    - my_keywords.py           # 顶层关键字模块
    - another_module.py        # 顶层关键字模块
    - web/                     # 子目录（可选作为子包）
      - __init__.py            # 可选，如果要作为子包导入
      - selenium_keywords.py   # 子目录中的关键字模块

每个关键字模块中应使用keyword_manager.register装饰器注册关键字。
"""

import importlib
import importlib.util
import importlib.metadata
import pkgutil
import os
import sys
from pathlib import Path
from typing import List

from pytest_dsl.core.keyword_manager import keyword_manager


def discover_installed_plugins() -> List[str]:
    """
    发现所有已安装的pytest-dsl关键字插件

    通过entry_points机制查找所有声明了'pytest_dsl.keywords'入口点的包

    Returns:
        List[str]: 已安装的插件包名列表
    """
    plugins = []
    try:
        # Python 3.10+ 支持 group 参数
        try:
            eps = importlib.metadata.entry_points(group='pytest_dsl.keywords')
        except TypeError:
            # Python 3.9 兼容性：不支持 group 参数，需要手动过滤
            all_eps = importlib.metadata.entry_points()
            eps = all_eps.get('pytest_dsl.keywords', [])

        for ep in eps:
            plugins.append(ep.module)
    except Exception as e:
        print(f"发现插件时出错: {e}")
    return plugins


def load_plugin_keywords(plugin_name: str) -> None:
    """
    加载指定插件包中的所有关键字
    
    Args:
        plugin_name: 插件包名
    """
    try:
        # 导入插件包
        plugin = importlib.import_module(plugin_name)
        
        # 如果插件有register_keywords函数，调用它
        if hasattr(plugin, 'register_keywords') and callable(plugin.register_keywords):
            # 创建一个包装的关键字管理器，自动添加来源信息
            class PluginKeywordManager:
                def __init__(self, original_manager, plugin_name):
                    self.original_manager = original_manager
                    self.plugin_name = plugin_name
                
                def register(self, name: str, parameters):
                    """带插件来源信息的注册方法"""
                    return self.original_manager.register_with_source(
                        name, parameters, 
                        source_type='plugin',
                        source_name=plugin_name,
                        module_name=plugin_name
                    )
                
                def __getattr__(self, name):
                    # 代理其他方法到原始管理器
                    return getattr(self.original_manager, name)
            
            plugin_manager = PluginKeywordManager(keyword_manager, plugin_name)
            plugin.register_keywords(plugin_manager)
            print(f"通过register_keywords加载插件: {plugin_name}")
            return
        
        # 否则，遍历包中的所有模块
        if hasattr(plugin, '__path__'):
            for _, name, is_pkg in pkgutil.iter_modules(plugin.__path__, plugin.__name__ + '.'):
                if not is_pkg:
                    try:
                        module = importlib.import_module(name)
                        print(f"加载插件模块: {name}")
                        # 模块已导入，关键字装饰器会自动注册
                        # 但我们需要在导入后更新来源信息
                        _update_keywords_source_info(plugin_name, name)
                    except ImportError as e:
                        print(f"无法导入模块 {name}: {e}")
    except ImportError as e:
        print(f"无法导入插件 {plugin_name}: {e}")


def _update_keywords_source_info(plugin_name: str, module_name: str):
    """更新模块中关键字的来源信息"""
    # 找到可能是新注册的关键字
    for keyword_name, keyword_info in keyword_manager._keywords.items():
        if keyword_info.get('module_name') == module_name:
            # 更新来源信息
            keyword_info.update({
                'source_type': 'plugin',
                'source_name': plugin_name,
                'plugin_module': module_name
            })


def load_all_plugins() -> None:
    """
    发现并加载所有已安装的关键字插件
    """
    plugins = discover_installed_plugins()
    for plugin_name in plugins:
        load_plugin_keywords(plugin_name)


def _load_module_from_file(file_path):
    """
    从文件路径动态加载Python模块
    
    Args:
        file_path: Python文件路径
    
    Returns:
        加载成功返回True，否则返回False
    """
    try:
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"已加载项目关键字模块: {module_name}")
            return True
    except Exception as e:
        print(f"加载项目关键字模块 {file_path.name} 时出错: {e}")
        return False


def scan_local_keywords() -> None:
    """
    扫描本地keywords目录中的关键字
    
    再查找并导入用户项目根目录下的keywords目录中的Python模块
    """
    # 2. 查找并导入用户项目中的keywords目录
    try:
        # 获取当前工作目录，通常是用户项目的根目录
        project_root = Path(os.getcwd())
        keywords_dir = project_root / 'keywords'
        
        if keywords_dir.exists() and keywords_dir.is_dir():
            print(f"发现项目关键字目录: {keywords_dir}")
            
            # 将keywords目录添加到Python路径中，以便能够导入
            if str(keywords_dir) not in sys.path:
                sys.path.insert(0, str(keywords_dir))
            
            # 首先尝试作为包导入整个keywords目录
            if (keywords_dir / '__init__.py').exists():
                try:
                    importlib.import_module('keywords')
                    print("已加载项目keywords包")
                except ImportError as e:
                    print(f"导入项目keywords包失败: {e}")
            
            # 遍历keywords目录下的所有Python文件（包括子目录）
            loaded_modules = 0
            
            # 先加载顶层目录中的模块
            for file_path in keywords_dir.glob('*.py'):
                if file_path.name != '__init__.py':
                    if _load_module_from_file(file_path):
                        loaded_modules += 1
            
            # 然后遍历子目录
            for subdir in [d for d in keywords_dir.iterdir() if d.is_dir()]:
                # 检查子目录是否为Python包
                init_file = subdir / '__init__.py'
                if init_file.exists():
                    # 尝试作为包导入
                    subdir_name = subdir.name
                    try:
                        importlib.import_module(f'keywords.{subdir_name}')
                        print(f"已加载项目关键字子包: {subdir_name}")
                        loaded_modules += 1
                    except ImportError as e:
                        print(f"导入项目关键字子包 {subdir_name} 失败: {e}")
                
                # 无论是否为包，都尝试直接加载其中的Python文件
                for file_path in subdir.glob('*.py'):
                    if file_path.name != '__init__.py':
                        if _load_module_from_file(file_path):
                            loaded_modules += 1
            
            if loaded_modules > 0:
                print(f"成功从项目中加载了 {loaded_modules} 个关键字模块")
            else:
                print("未从项目中加载到任何关键字模块")
        else:
            print("提示: 未在项目中找到keywords目录")
    except Exception as e:
        print(f"扫描项目关键字时出错: {e}")


if __name__ == "__main__":
    load_all_plugins()