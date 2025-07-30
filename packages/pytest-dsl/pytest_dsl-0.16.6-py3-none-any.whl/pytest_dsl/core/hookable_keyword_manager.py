"""
可扩展的关键字管理器

支持通过hook机制注册自定义关键字
"""
import threading
from typing import Dict, List, Optional, Any
from .keyword_manager import keyword_manager
from .hook_manager import hook_manager


class HookableKeywordManager:
    """支持Hook机制的关键字管理器"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # 只初始化一次，避免重复初始化
        if hasattr(self, '_initialized_instance'):
            return
        self.hook_keywords = {}  # 存储通过hook注册的关键字
        self._initialized = False
        self._initialized_instance = True

    def initialize(self, force_reload: bool = False):
        """初始化，调用hook注册关键字

        Args:
            force_reload: 是否强制重新初始化，即使已经初始化过
        """
        if self._initialized and not force_reload:
            return

        if hook_manager and hook_manager._initialized:
            try:
                # 调用hook注册自定义关键字
                hook_manager.pm.hook.dsl_register_custom_keywords()
                print(f"通过Hook注册了 {len(self.hook_keywords)} 个自定义关键字")
            except Exception as e:
                print(f"Hook关键字注册失败: {e}")

        self._initialized = True

    def reinitialize_after_plugin_load(self):
        """在插件加载后重新初始化hookable关键字管理器

        这个方法专门用于pytest环境下，在新插件加载后重新初始化
        """
        if hook_manager and hook_manager._initialized:
            try:
                print("重新执行Hook关键字注册...")
                # 重新调用hook注册自定义关键字
                hook_manager.pm.hook.dsl_register_custom_keywords()
                print(f"重新注册完成，当前Hook关键字数量: {len(self.hook_keywords)}")
            except Exception as e:
                print(f"重新执行Hook关键字注册失败: {e}")

    def register_hook_keyword(self, keyword_name: str, dsl_content: str,
                              source_info: Optional[Dict[str, Any]] = None):
        """通过Hook注册自定义关键字

        Args:
            keyword_name: 关键字名称
            dsl_content: DSL内容定义
            source_info: 来源信息
        """
        # 检查是否已经注册过
        if keyword_name in self.hook_keywords:
            print(f"Hook关键字 {keyword_name} 已存在，跳过重复注册")
            return

        # 使用custom_keyword_manager的公共方法注册关键字
        try:
            from .custom_keyword_manager import custom_keyword_manager

            # 准备来源名称
            source_name = (source_info.get('source_name', 'Hook插件') 
                          if source_info else 'Hook插件')

            # 使用公共方法注册指定关键字
            success = custom_keyword_manager.register_specific_keyword_from_dsl_content(
                keyword_name, dsl_content, source_name
            )

            if success:
                # 更新来源信息
                if keyword_name in keyword_manager._keywords:
                    keyword_info = keyword_manager._keywords[keyword_name]
                    if source_info:
                        keyword_info.update(source_info)
                    else:
                        keyword_info.update({
                            'source_type': 'hook',
                            'source_name': 'Hook插件'
                        })

                # 记录到hook关键字列表
                self.hook_keywords[keyword_name] = {
                    'dsl_content': dsl_content,
                    'source_info': source_info or {
                        'source_type': 'hook',
                        'source_name': 'Hook插件'
                    }
                }

                print(f"注册Hook关键字: {keyword_name}")

        except Exception as e:
            print(f"注册Hook关键字失败 {keyword_name}: {e}")
            raise

    def get_hook_keywords(self) -> Dict[str, Dict]:
        """获取所有通过Hook注册的关键字"""
        return self.hook_keywords.copy()

    def is_hook_keyword(self, keyword_name: str) -> bool:
        """检查是否为Hook关键字"""
        return keyword_name in self.hook_keywords

    def unregister_hook_keyword(self, keyword_name: str):
        """注销Hook关键字"""
        if keyword_name in self.hook_keywords:
            del self.hook_keywords[keyword_name]
            # 从关键字管理器中移除
            if hasattr(keyword_manager, '_keywords'):
                keyword_manager._keywords.pop(keyword_name, None)
            print(f"注销Hook关键字: {keyword_name}")


# 全局实例
hookable_keyword_manager = HookableKeywordManager()
