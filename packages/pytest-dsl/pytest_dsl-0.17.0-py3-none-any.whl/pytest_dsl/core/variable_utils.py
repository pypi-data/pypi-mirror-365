"""变量替换工具模块

该模块提供了高级的变量替换功能，支持复杂的变量访问语法。
"""

import re
import json
from typing import Any, Dict, List, Optional
from pytest_dsl.core.global_context import global_context
from pytest_dsl.core.context import TestContext


class VariableReplacer:
    """变量替换器，支持高级变量访问语法"""

    def __init__(self, local_variables: Dict[str, Any] = None, test_context: TestContext = None):
        """初始化变量替换器

        Args:
            local_variables: 本地变量字典
            test_context: 测试上下文
        """
        self.local_variables = local_variables or {}
        self._test_context = test_context

    @property
    def test_context(self) -> TestContext:
        """获取测试上下文，如果没有提供则尝试从关键字管理器获取"""
        if self._test_context:
            return self._test_context

        # 尝试从关键字管理器获取当前上下文
        try:
            from pytest_dsl.core.keyword_manager import keyword_manager
            return getattr(keyword_manager, 'current_context', None)
        except ImportError:
            return None

    def get_variable(self, var_name: str) -> Any:
        """获取变量值，按优先级顺序查找

        查找顺序：
        1. 本地变量
        2. 测试上下文
        3. 全局上下文（包含YAML变量的访问）

        Args:
            var_name: 变量名

        Returns:
            变量值

        Raises:
            KeyError: 当变量不存在时
        """
        # 从本地变量获取
        if var_name in self.local_variables:
            value = self.local_variables[var_name]
            return self._convert_value(value)

        # 从测试上下文中获取（优先级高于YAML变量）
        context = self.test_context
        if context and context.has(var_name):
            value = context.get(var_name)
            return self._convert_value(value)

        # 从全局上下文获取（包含对YAML变量的统一访问）
        if global_context.has_variable(var_name):
            value = global_context.get_variable(var_name)
            return self._convert_value(value)

        # 如果变量不存在，抛出异常
        raise KeyError(f"变量 '{var_name}' 不存在")

    def _convert_value(self, value: Any) -> Any:
        """转换值为正确的类型

        Args:
            value: 要转换的值

        Returns:
            转换后的值
        """
        if isinstance(value, str):
            # 处理布尔值
            if value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            # 处理数字
            try:
                if '.' in value:
                    return float(value)
                return int(value)
            except (ValueError, TypeError):
                pass
        return value

    def replace_in_string(self, value: str) -> Any:
        """替换字符串中的变量引用

        支持多种访问语法：
        - 基本变量: ${variable}
        - 点号访问: ${object.property}
        - 数组索引: ${array[0]}, ${array[-1]}
        - 字典键访问: ${dict["key"]}, ${dict['key']}
        - 混合访问: ${users[0].name}, ${data["users"][0]["name"]}

        Args:
            value: 包含变量引用的字符串

        Returns:
            替换后的字符串或原始对象（如果整个值是单一变量引用）

        Raises:
            KeyError: 当变量不存在时
        """
        if not isinstance(value, str) or '${' not in value:
            return value

        # 扩展的变量引用模式，支持数组索引和字典键访问
        # 匹配: ${variable}, ${obj.prop}, ${arr[0]}, ${dict["key"]}, ${obj[0].prop} 等
        pattern = r'\$\{([a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*(?:(?:\.[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)|(?:\[[^\]]+\]))*)\}'

        # 检查是否整个字符串就是一个变量引用
        full_match = re.fullmatch(pattern, value)
        if full_match:
            # 如果整个字符串就是一个变量引用，直接返回变量值（保持原始类型）
            var_ref = full_match.group(1)
            try:
                return self._parse_variable_path(var_ref)
            except (KeyError, IndexError, TypeError) as e:
                raise KeyError(f"无法解析变量引用 '${{{var_ref}}}': {str(e)}")

        # 如果字符串中包含多个变量引用或混合了字面量，进行字符串替换
        result = value
        matches = list(re.finditer(pattern, result))

        # 从后向前替换，避免位置偏移
        for match in reversed(matches):
            var_ref = match.group(1)  # 例如: "users[0].name" 或 "data['key']"

            try:
                var_value = self._parse_variable_path(var_ref)
                # 替换变量引用，转换为字符串
                result = result[:match.start()] + str(var_value) + \
                    result[match.end():]
            except (KeyError, IndexError, TypeError) as e:
                raise KeyError(f"无法解析变量引用 '${{{var_ref}}}': {str(e)}")

        return result

    def _parse_variable_path(self, var_ref: str):
        """解析复杂的变量访问路径

        支持的语法：
        - variable
        - object.property
        - array[0]
        - dict["key"]
        - users[0].name
        - data["users"][0]["name"]

        Args:
            var_ref: 变量引用路径，如 "users[0].name"

        Returns:
            解析后的变量值

        Raises:
            KeyError: 当变量不存在时
            IndexError: 当数组索引超出范围时
            TypeError: 当类型不匹配时
        """
        # 解析访问路径
        path_parts = self._tokenize_path(var_ref)

        # 获取根变量
        root_var_name = path_parts[0]
        try:
            current_value = self.get_variable(root_var_name)
        except KeyError:
            raise KeyError(f"变量 '{root_var_name}' 不存在")

        # 逐步访问路径
        for part in path_parts[1:]:
            current_value = self._access_value(
                current_value, part, root_var_name)

        return current_value

    def _tokenize_path(self, var_ref: str) -> list:
        """将变量路径分解为访问令牌

        例如：
        - "users[0].name" -> ["users", "[0]", "name"]
        - "data['key'].items[1]" -> ["data", "['key']", "items", "[1]"]

        Args:
            var_ref: 变量引用路径

        Returns:
            访问令牌列表
        """
        tokens = []
        current_token = ""
        i = 0

        while i < len(var_ref):
            char = var_ref[i]

            if char == '.':
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            elif char == '[':
                if current_token:
                    tokens.append(current_token)
                    current_token = ""

                # 找到匹配的右括号
                bracket_count = 1
                bracket_content = "["
                i += 1

                while i < len(var_ref) and bracket_count > 0:
                    char = var_ref[i]
                    bracket_content += char
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                    i += 1

                tokens.append(bracket_content)
                i -= 1  # 回退一位，因为外层循环会自增
            else:
                current_token += char

            i += 1

        if current_token:
            tokens.append(current_token)

        return tokens

    def _access_value(self, current_value, access_token: str, root_var_name: str):
        """根据访问令牌获取值

        Args:
            current_value: 当前值
            access_token: 访问令牌，如 "name", "[0]", "['key']"
            root_var_name: 根变量名（用于错误信息）

        Returns:
            访问后的值

        Raises:
            KeyError: 当键不存在时
            IndexError: 当索引超出范围时
            TypeError: 当类型不匹配时
        """
        if access_token.startswith('[') and access_token.endswith(']'):
            # 数组索引或字典键访问
            key_content = access_token[1:-1].strip()

            # 处理字符串键（带引号）
            if (key_content.startswith('"') and key_content.endswith('"')) or \
               (key_content.startswith("'") and key_content.endswith("'")):
                key = key_content[1:-1]  # 去掉引号
                if isinstance(current_value, dict):
                    if key not in current_value:
                        raise KeyError(f"字典中不存在键 '{key}'")
                    return current_value[key]
                else:
                    raise TypeError(
                        f"无法在 {type(current_value).__name__} 类型上使用字符串键访问")

            # 处理数字索引
            try:
                index = int(key_content)
                if isinstance(current_value, (list, tuple)):
                    if index >= len(current_value) or index < -len(current_value):
                        raise IndexError(
                            f"数组索引 {index} 超出范围，数组长度为 {len(current_value)}")
                    return current_value[index]
                elif isinstance(current_value, dict):
                    # 字典也可以用数字键
                    str_key = str(index)
                    if str_key not in current_value and index not in current_value:
                        raise KeyError(f"字典中不存在键 '{index}' 或 '{str_key}'")
                    return current_value.get(index, current_value.get(str_key))
                else:
                    raise TypeError(
                        f"无法在 {type(current_value).__name__} 类型上使用索引访问")
            except ValueError:
                raise ValueError(f"无效的索引格式: '{key_content}'")

        else:
            # 属性访问（点号语法）
            if isinstance(current_value, dict) and access_token in current_value:
                return current_value[access_token]
            else:
                raise KeyError(
                    f"无法访问属性 '{access_token}'，当前值类型是 {type(current_value).__name__}")

    def replace_in_dict(self, data: Dict[str, Any], visited: Optional[set] = None) -> Dict[str, Any]:
        """递归替换字典中的变量引用

        Args:
            data: 包含变量引用的字典
            visited: 已访问对象的集合，用于检测循环引用

        Returns:
            替换后的字典

        Raises:
            KeyError: 当变量不存在时
        """
        if not isinstance(data, dict):
            return data

        # 初始化访问集合
        if visited is None:
            visited = set()

        # 检测循环引用
        data_id = id(data)
        if data_id in visited:
            return {"<循环引用>": f"字典对象 {type(data).__name__}"}

        visited.add(data_id)
        try:
            result = {}
            for key, value in data.items():
                # 替换键中的变量
                new_key = self.replace_in_string(
                    key) if isinstance(key, str) else key
                # 替换值中的变量
                new_value = self.replace_in_value(value, visited)
                result[new_key] = new_value

            return result
        finally:
            visited.discard(data_id)

    def replace_in_list(self, data: List[Any], visited: Optional[set] = None) -> List[Any]:
        """递归替换列表中的变量引用

        Args:
            data: 包含变量引用的列表
            visited: 已访问对象的集合，用于检测循环引用

        Returns:
            替换后的列表

        Raises:
            KeyError: 当变量不存在时
        """
        if not isinstance(data, list):
            return data

        # 初始化访问集合
        if visited is None:
            visited = set()

        # 检测循环引用
        data_id = id(data)
        if data_id in visited:
            return [f"<循环引用: 列表对象 {type(data).__name__}>"]

        visited.add(data_id)
        try:
            return [self.replace_in_value(item, visited) for item in data]
        finally:
            visited.discard(data_id)

    def replace_in_value(self, value: Any, visited: Optional[set] = None) -> Any:
        """递归替换任意值中的变量引用

        Args:
            value: 任意值，可能是字符串、字典、列表等
            visited: 已访问对象的集合，用于检测循环引用

        Returns:
            替换后的值

        Raises:
            KeyError: 当变量不存在时
        """
        if isinstance(value, str):
            return self.replace_in_string(value)
        elif isinstance(value, dict):
            return self.replace_in_dict(value, visited)
        elif isinstance(value, list):
            return self.replace_in_list(value, visited)
        elif isinstance(value, (int, float, bool, type(None))):
            return value
        else:
            # 对于其他类型，尝试转换为字符串后替换
            try:
                str_value = str(value)
                if '${' in str_value:
                    replaced = self.replace_in_string(str_value)
                    # 尝试将替换后的字符串转换回原始类型
                    if isinstance(value, (int, float)):
                        return type(value)(replaced)
                    elif isinstance(value, bool):
                        return replaced.lower() == 'true'
                    return replaced
                return value
            except:
                return value

    def replace_in_json(self, json_str: str) -> str:
        """替换JSON字符串中的变量引用

        Args:
            json_str: 包含变量引用的JSON字符串

        Returns:
            替换后的JSON字符串

        Raises:
            KeyError: 当变量不存在时
            json.JSONDecodeError: 当JSON解析失败时
        """
        try:
            # 先解析JSON
            data = json.loads(json_str)
            # 替换变量
            replaced_data = self.replace_in_value(data)
            # 重新序列化为JSON
            return json.dumps(replaced_data, ensure_ascii=False)
        except json.JSONDecodeError:
            # 如果JSON解析失败，直接作为字符串处理
            return self.replace_in_string(json_str)

    def replace_in_yaml(self, yaml_str: str) -> str:
        """替换YAML字符串中的变量引用

        Args:
            yaml_str: 包含变量引用的YAML字符串

        Returns:
            替换后的YAML字符串

        Raises:
            KeyError: 当变量不存在时
        """
        try:
            import yaml
            # 先解析YAML
            data = yaml.safe_load(yaml_str)
            # 替换变量
            replaced_data = self.replace_in_value(data)
            # 重新序列化为YAML
            return yaml.dump(replaced_data, allow_unicode=True)
        except:
            # 如果YAML解析失败，直接作为字符串处理
            return self.replace_in_string(yaml_str)
