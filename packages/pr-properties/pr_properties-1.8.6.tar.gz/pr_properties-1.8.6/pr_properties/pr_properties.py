import os
import shutil
import uuid
from typing import Optional, Dict, Any, Union

import filelock


class PropertiesHandler:
    """
    Properties 文件处理器，用于读取、写入和管理 properties 格式的配置文件。

    支持文件锁机制，确保多进程/多线程环境下的文件安全访问。
    """

    def __init__(self, file_path: Optional[str] = None) -> None:
        """
        初始化 PropertiesHandler 对象。

        :param file_path: 文件路径，如果为 None 则需要在后续操作中指定
        :type file_path: Optional[str]
        """
        self.file_path: Optional[str] = file_path
        self.properties: Dict[str, Any] = {}

    def backup(self) -> None:
        """
        创建文件备份。

        如果备份文件不存在，则创建一个 .pr_bak 后缀的备份文件。

        :raises Exception: 当备份过程中发生 IO 错误时抛出异常
        """
        if not self.file_path:
            raise ValueError("文件路径未设置")

        backup_file_path = self.file_path + '.pr_bak'
        if not os.path.exists(backup_file_path):
            try:
                shutil.copy2(self.file_path, backup_file_path)
            except IOError as e:
                raise Exception(f"备份文件时出现错误：{e}") from e

    def _read(self, encoding: str = 'utf-8', ignore_errors: bool = False) -> 'PropertiesHandler':
        """
        内部读取方法，解析 properties 文件内容。

        :param encoding: 文件编码格式
        :type encoding: str
        :param ignore_errors: 是否忽略编码错误
        :type ignore_errors: bool
        :return: 返回当前对象实例，支持链式调用
        :rtype: PropertiesHandler
        :raises FileNotFoundError: 当文件不存在时抛出
        :raises Exception: 当读取过程中发生 IO 错误时抛出异常
        """
        if not self.file_path or not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件路径不存在: {self.file_path}")

        lock = filelock.FileLock(self.file_path + '.lock')

        try:
            with lock.acquire(timeout=10):
                with open(self.file_path, 'r', encoding=encoding,
                          errors='ignore' if ignore_errors else 'strict') as file:
                    lines = file.readlines()

            self._parse_lines(lines)

        except IOError as e:
            raise Exception(f"读取文件时出现错误：{e}") from e
        finally:
            # 确保文件锁被释放
            if lock.is_locked:
                lock.release()

        return self

    def _parse_lines(self, lines: list) -> None:
        """
        解析文件行内容到 properties 字典。

        :param lines: 文件行列表
        :type lines: list
        """
        for line in lines:
            line = line.strip()

            # 处理空行
            if not line:
                key = str(uuid.uuid4())  # 使用UUID作为空行标识
                self.properties[key] = None
                continue

            # 处理注释行
            if line.startswith('#') or line.startswith(';'):
                self.properties[line] = ""
                continue

            # 解析键值对
            self._parse_key_value(line)

    def _parse_key_value(self, line: str) -> None:
        """
        解析单行的键值对。

        :param line: 待解析的行内容
        :type line: str
        """
        key_value = line.split('=', 1)  # 只分割第一个等号

        if len(key_value) == 1:
            # 只有键没有值的情况
            self.properties[key_value[0].strip()] = ""
            return

        key = key_value[0].strip()
        value = key_value[1].strip() if len(key_value) > 1 else ""
        self.properties[key] = value

    def read(self, file_path: Optional[str] = None, encoding: str = 'utf-8',
             ignore_errors: bool = False) -> 'PropertiesHandler':
        """
        读取 properties 文件内容。

        :param file_path: 指定要读取的文件路径，如果为 None，则使用对象初始化时指定的路径
        :type file_path: Optional[str]
        :param encoding: 读取文件时使用的编码格式，默认为 'utf-8'
        :type encoding: str
        :param ignore_errors: 是否忽略读取过程中出现的编码错误，默认为 False
        :type ignore_errors: bool
        :return: 返回当前对象实例，支持链式调用
        :rtype: PropertiesHandler
        """
        if file_path is not None:
            self.file_path = file_path

        # 重新初始化 properties 字典
        self.properties.clear()

        return self._read(encoding=encoding, ignore_errors=ignore_errors)

    def write(self) -> None:
        """
        将当前 properties 写入文件。

        写入前会自动创建备份文件。

        :raises ValueError: 当文件路径未设置时抛出
        :raises Exception: 当写入过程中发生 IO 错误时抛出异常
        """
        if not self.file_path:
            raise ValueError("文件路径未设置")

        self.backup()

        lock = filelock.FileLock(self.file_path + '.lock')

        try:
            with lock.acquire(timeout=10):
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    file.write(str(self))
        except IOError as e:
            raise Exception(f"写入文件时出现错误：{e}") from e
        finally:
            # 确保文件锁被释放
            if lock.is_locked:
                lock.release()

    def __getitem__(self, key: Union[str, int]) -> Any:
        """
        获取属性值（字典风格访问）。

        :param key: 属性键
        :type key: Union[str, int]
        :return: 属性值
        :rtype: Any
        :raises KeyError: 当键不存在时抛出
        """
        return self.properties[str(key)]

    def __setitem__(self, key: Union[str, int], value: Any) -> None:
        """
        设置属性值（字典风格赋值）。

        :param key: 属性键
        :type key: Union[str, int]
        :param value: 属性值
        :type value: Any
        """
        self.properties[str(key)] = value

    def __delitem__(self, key: Union[str, int]) -> None:
        """
        删除属性（字典风格删除）。

        :param key: 属性键
        :type key: Union[str, int]
        :raises KeyError: 当键不存在时抛出
        """
        del self.properties[str(key)]

    def get(self, key: Union[str, int], default: Any = None) -> Any:
        """
        获取属性值，如果属性不存在则返回默认值。

        :param key: 属性键
        :type key: Union[str, int]
        :param default: 默认值，当键不存在时返回
        :type default: Any
        :return: 属性值或默认值
        :rtype: Any
        """
        return self.properties.get(str(key), default)

    def __str__(self) -> str:
        """
        将 properties 转换为字符串格式。

        :return: properties 格式的字符串
        :rtype: str
        """
        output_lines = []

        for key, value in self.properties.items():
            if value is None:
                # None 值表示空行
                output_lines.append("")
            elif value == "":
                # 空字符串值表示注释行或只有键的行
                output_lines.append(str(key))
            else:
                # 正常的键值对
                output_lines.append(f"{key} = {value}")

        return '\n'.join(output_lines).rstrip('\n')

    def __len__(self) -> int:
        """
        返回 properties 的数量。

        :return: 属性数量
        :rtype: int
        """
        return len(self.properties)

    def keys(self):
        """
        返回所有键。

        :return: 键的视图
        """
        return self.properties.keys()

    def values(self):
        """
        返回所有值。

        :return: 值的视图
        """
        return self.properties.values()

    def items(self):
        """
        返回所有键值对。

        :return: 键值对的视图
        """
        return self.properties.items()


# 全局实例，用于简单场景
# 注意：多线程环境下请勿使用此单例模式，建议为每个线程创建独立实例
pr_properties = PropertiesHandler()
