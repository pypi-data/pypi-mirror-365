# pr_properties

一个轻量级的 Python properties 文件处理库，支持线程安全的读写操作。

## 安装

```bash
pip install pr-properties
```

## 快速开始

```python
from pr_properties import PropertiesHandler

# 读取配置文件
props = PropertiesHandler('config.properties')
props.read()

# 获取/设置值
value = props.get('key', 'default')
props['new_key'] = 'new_value'

# 保存文件
props.write()
```

## 特性

- 🔒 线程安全的文件操作
- 📝 支持注释和空行
- 🔄 自动备份机制
- 🎯 字典风格的 API

## 基本用法

### 读取文件

```python
props = PropertiesHandler()
props.read('config.properties', encoding='utf-8')
```

### 操作属性

```python
# 获取值
host = props.get('database.host', 'localhost')
port = props['server.port']

# 设置值
props['app.name'] = 'MyApp'
props['debug'] = 'true'

# 删除
del props['old_key']
```

### 保存文件

```python
props.write()  # 自动创建 .pr_bak 备份
```

## Properties 格式

```properties
# 注释行
database.host=localhost
database.port=5432

# 应用配置
app.name=My Application
app.debug=false
```

## 线程安全

多线程环境下为每个线程创建独立实例：

```python
# 推荐
props = PropertiesHandler('config.properties')

# 避免在多线程中使用全局实例
from pr_properties import pr_properties  # 单线程可用
```

## 依赖

- Python >= 3.7
- filelock == 3.12.2

## 许可证

Apache License 2.0