# Python os 和 sys 模块使用指南

## 概述

`os` 和 `sys` 是 Python 标准库中两个重要的模块，用于系统交互和系统参数访问。

- **`os` 模块**：提供与操作系统交互的功能（文件系统、环境变量、进程管理等）
- **`sys` 模块**：提供与 Python 解释器交互的功能（命令行参数、路径、版本信息等）

---

## os 模块

### 1. 路径操作

#### 获取当前工作目录

```python
import os

# 获取当前工作目录
current_dir = os.getcwd()
print(f"当前目录: {current_dir}")
```

#### 改变工作目录

```python
# 切换到指定目录
os.chdir('/path/to/directory')

# 切换回原目录（保存之前的位置）
original_dir = os.getcwd()
os.chdir('/new/path')
# ... 执行操作 ...
os.chdir(original_dir)  # 恢复
```

#### 路径拼接和拆分

```python
# 路径拼接（推荐使用，跨平台兼容）
file_path = os.path.join('data', 'output', 'result.txt')
# Windows: data\output\result.txt
# Linux/Mac: data/output/result.txt

# 路径拆分
directory, filename = os.path.split(file_path)
# directory: 'data/output'
# filename: 'result.txt'

# 获取目录名和文件名
dirname = os.path.dirname(file_path)  # 'data/output'
basename = os.path.basename(file_path)  # 'result.txt'

# 分离文件名和扩展名
name, ext = os.path.splitext('file.txt')
# name: 'file'
# ext: '.txt'
```

#### 路径规范化

```python
# 获取绝对路径
abs_path = os.path.abspath('relative/path/file.txt')

# 规范化路径（处理 .. 和 .）
normalized = os.path.normpath('data/../output/./file.txt')
# 结果: 'output/file.txt'

# 展开用户目录
user_path = os.path.expanduser('~/documents/file.txt')
# Windows: C:\Users\Username\documents\file.txt
# Linux/Mac: /home/username/documents/file.txt
```

### 2. 文件和目录操作

#### 检查路径是否存在

```python
# 检查文件或目录是否存在
if os.path.exists('/path/to/file'):
    print("路径存在")

# 检查是否为文件
if os.path.isfile('/path/to/file.txt'):
    print("是文件")

# 检查是否为目录
if os.path.isdir('/path/to/directory'):
    print("是目录")

# 检查是否为链接
if os.path.islink('/path/to/link'):
    print("是符号链接")
```

#### 创建和删除目录

```python
# 创建单个目录
os.mkdir('new_directory')

# 创建多级目录（如果父目录不存在会自动创建）
os.makedirs('path/to/new/directory', exist_ok=True)
# exist_ok=True: 如果目录已存在不会报错

# 删除空目录
os.rmdir('empty_directory')

# 删除多级目录（递归删除）
import shutil
shutil.rmtree('directory_with_contents')
```

#### 列出目录内容

```python
# 列出目录中的所有文件和文件夹
items = os.listdir('/path/to/directory')
for item in items:
    print(item)

# 使用 os.walk() 递归遍历目录树
for root, dirs, files in os.walk('/path/to/directory'):
    print(f"当前目录: {root}")
    print(f"子目录: {dirs}")
    print(f"文件: {files}")
```

#### 文件操作

```python
# 重命名文件或目录
os.rename('old_name.txt', 'new_name.txt')

# 删除文件
os.remove('file_to_delete.txt')

# 获取文件大小
file_size = os.path.getsize('file.txt')
print(f"文件大小: {file_size} 字节")

# 获取文件修改时间
import time
mtime = os.path.getmtime('file.txt')
print(f"修改时间: {time.ctime(mtime)}")
```

### 3. 环境变量

#### 获取环境变量

```python
# 获取环境变量
home = os.environ.get('HOME')  # Linux/Mac
home = os.environ.get('USERPROFILE')  # Windows

# 获取所有环境变量
for key, value in os.environ.items():
    print(f"{key}: {value}")

# 安全获取（带默认值）
python_path = os.environ.get('PYTHONPATH', '/default/path')
```

#### 设置环境变量

```python
# 设置环境变量（仅当前进程）
os.environ['MY_VAR'] = 'my_value'

# 检查环境变量是否存在
if 'MY_VAR' in os.environ:
    print("环境变量存在")
```

### 4. 进程管理

```python
# 获取当前进程 ID
pid = os.getpid()
print(f"进程 ID: {pid}")

# 获取父进程 ID
ppid = os.getppid()
print(f"父进程 ID: {ppid}")

# 执行系统命令（不推荐，使用 subprocess 更好）
result = os.system('ls -l')  # Linux/Mac
result = os.system('dir')    # Windows

# 获取命令输出（已废弃，使用 subprocess）
output = os.popen('ls').read()
```

### 5. 路径属性检查

```python
# 检查路径是否为绝对路径
is_abs = os.path.isabs('/absolute/path')  # True
is_abs = os.path.isabs('relative/path')    # False

# 检查路径是否相同（处理符号链接）
same = os.path.samefile('/path1', '/path2')
```

---

## sys 模块

### 1. 命令行参数

#### 获取命令行参数

```python
import sys

# sys.argv 是一个列表，包含命令行参数
# sys.argv[0] 是脚本名称
# sys.argv[1:] 是传递给脚本的参数

# 示例：python script.py arg1 arg2 arg3
script_name = sys.argv[0]  # 'script.py'
arguments = sys.argv[1:]   # ['arg1', 'arg2', 'arg3']

# 完整示例
if len(sys.argv) > 1:
    print(f"脚本名称: {sys.argv[0]}")
    print(f"参数: {sys.argv[1:]}")
else:
    print("没有提供参数")
```

#### 解析命令行参数（推荐使用 argparse）

```python
import sys
import argparse

parser = argparse.ArgumentParser(description='处理命令行参数')
parser.add_argument('input_file', help='输入文件路径')
parser.add_argument('--output', '-o', help='输出文件路径')
parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')

args = parser.parse_args()
print(f"输入文件: {args.input_file}")
if args.output:
    print(f"输出文件: {args.output}")
```

### 2. Python 路径管理

#### sys.path

```python
# sys.path 是 Python 搜索模块的路径列表
print("Python 搜索路径:")
for path in sys.path:
    print(f"  - {path}")

# 添加自定义路径到搜索路径
sys.path.insert(0, '/custom/module/path')
# 或
sys.path.append('/another/custom/path')

# 在项目中使用（常见模式）
import os
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
```

#### 动态导入模块

```python
# 添加路径后导入自定义模块
sys.path.insert(0, '/path/to/custom/modules')
import my_custom_module
```

### 3. 标准输入输出

#### 标准输入输出流

```python
# 写入标准输出
sys.stdout.write("Hello, World!\n")
sys.stdout.flush()  # 立即刷新缓冲区

# 写入标准错误
sys.stderr.write("错误信息\n")

# 从标准输入读取
user_input = sys.stdin.readline().strip()
print(f"用户输入: {user_input}")

# 重定向输出（临时）
original_stdout = sys.stdout
with open('output.txt', 'w') as f:
    sys.stdout = f
    print("这会被写入文件")
sys.stdout = original_stdout  # 恢复
```

### 4. 系统信息

#### Python 版本信息

```python
# 获取 Python 版本
print(f"Python 版本: {sys.version}")
print(f"版本信息: {sys.version_info}")
# sys.version_info 是 namedtuple: (major, minor, micro, releaselevel, serial)

# 检查 Python 版本
if sys.version_info >= (3, 8):
    print("Python 3.8 或更高版本")
else:
    print("需要 Python 3.8 或更高版本")
```

#### 平台信息

```python
# 获取操作系统平台
platform = sys.platform
print(f"平台: {platform}")
# 常见值: 'win32', 'linux', 'darwin' (Mac), 'cygwin'

# 根据平台执行不同代码
if sys.platform == 'win32':
    print("Windows 系统")
elif sys.platform == 'linux':
    print("Linux 系统")
elif sys.platform == 'darwin':
    print("macOS 系统")
```

#### 系统信息

```python
# 获取默认编码
default_encoding = sys.getdefaultencoding()
print(f"默认编码: {default_encoding}")

# 获取文件系统编码
filesystem_encoding = sys.getfilesystemencoding()
print(f"文件系统编码: {filesystem_encoding}")

# 获取最大整数值
max_int = sys.maxsize
print(f"最大整数: {max_int}")
```

### 5. 退出程序

```python
# 正常退出
sys.exit(0)  # 0 表示成功

# 异常退出
sys.exit(1)  # 非零值表示错误

# 带消息退出
sys.exit("程序异常终止")

# 在 try-except 中使用
try:
    # 执行操作
    pass
except Exception as e:
    print(f"错误: {e}")
    sys.exit(1)
```

### 6. 模块和导入

```python
# 获取已导入的模块
imported_modules = sys.modules.keys()
print(f"已导入模块数量: {len(sys.modules)}")

# 检查模块是否已导入
if 'pandas' in sys.modules:
    print("pandas 已导入")

# 获取模块对象
if 'os' in sys.modules:
    os_module = sys.modules['os']
    print(f"os 模块位置: {os_module.__file__}")
```

---

## 常用组合模式

### 1. 获取脚本所在目录

```python
import os
import sys

# 方法 1: 使用 __file__（推荐）
script_dir = os.path.dirname(os.path.abspath(__file__))
print(f"脚本目录: {script_dir}")

# 方法 2: 使用 sys.argv[0]
script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
print(f"脚本目录: {script_dir}")

# 添加到 Python 路径
sys.path.insert(0, script_dir)
```

### 2. 跨平台路径处理

```python
import os
import sys

# 根据平台选择路径分隔符
if sys.platform == 'win32':
    data_dir = os.path.join('C:', 'Users', 'Username', 'Data')
else:
    data_dir = os.path.join('/home', 'username', 'data')

# 使用 os.path.join 自动处理（推荐）
data_dir = os.path.join('data', 'output', 'results')
```

### 3. 环境变量配置

```python
import os
import sys

# 从环境变量读取配置
minio_endpoint = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
minio_access_key = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
minio_secret_key = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')

# 设置环境变量（如果需要）
os.environ['PYTHONPATH'] = '/custom/path'
```

### 4. 日志和错误处理

```python
import os
import sys

# 创建日志目录
log_dir = os.path.join(os.getcwd(), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 重定向错误输出到文件
log_file = os.path.join(log_dir, 'error.log')
sys.stderr = open(log_file, 'w')
```

### 5. 项目根目录设置

```python
import os
import sys

# 获取项目根目录（假设脚本在项目子目录中）
def get_project_root():
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    # 向上查找直到找到项目根目录（例如包含 .git 或 requirements.txt）
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return current_dir

project_root = get_project_root()
sys.path.insert(0, project_root)
```

---

## 实际应用示例

### 示例 1: 文件处理脚本

```python
import os
import sys

def process_files(input_dir, output_dir):
    """处理目录中的所有文件"""
    # 检查输入目录是否存在
    if not os.path.isdir(input_dir):
        print(f"错误: 输入目录不存在: {input_dir}")
        sys.exit(1)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 遍历文件
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)
        if os.path.isfile(file_path):
            # 处理文件
            print(f"处理文件: {filename}")
            # ... 处理逻辑 ...

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python script.py <输入目录> <输出目录>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    process_files(input_dir, output_dir)
```

### 示例 2: 配置加载

```python
import os
import sys

def load_config():
    """从环境变量或配置文件加载配置"""
    config = {
        'endpoint': os.environ.get('MINIO_ENDPOINT', 'localhost:9000'),
        'access_key': os.environ.get('MINIO_ACCESS_KEY', 'minioadmin'),
        'secret_key': os.environ.get('MINIO_SECRET_KEY', 'minioadmin'),
    }
    
    # 检查必要的配置
    required_keys = ['endpoint', 'access_key', 'secret_key']
    missing = [key for key in required_keys if not config[key]]
    
    if missing:
        print(f"错误: 缺少必要的配置: {', '.join(missing)}")
        sys.exit(1)
    
    return config

if __name__ == '__main__':
    config = load_config()
    print(f"配置加载成功: {config['endpoint']}")
```

### 示例 3: 路径解析和模块导入

```python
import os
import sys

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

# 添加项目根目录到 Python 路径
sys.path.insert(0, project_root)

# 现在可以导入项目模块
try:
    from Lib import action
    from Lib import json_yaml_IO
    print("模块导入成功")
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)
```

---

## 注意事项

### 1. 路径分隔符

- **不要硬编码路径分隔符**：使用 `os.path.join()` 而不是 `'/'` 或 `'\'`
- **跨平台兼容性**：`os.path.join()` 自动处理不同操作系统的路径分隔符

### 2. 文件操作

- **检查路径存在性**：在操作文件前先检查路径是否存在
- **异常处理**：文件操作可能失败，使用 try-except 处理异常
- **资源管理**：使用 `with` 语句确保文件正确关闭

### 3. 环境变量

- **安全性**：不要在代码中硬编码敏感信息，使用环境变量
- **默认值**：使用 `os.environ.get(key, default)` 提供默认值

### 4. sys.path 修改

- **临时修改**：`sys.path` 的修改是全局的，注意影响范围
- **项目结构**：考虑使用相对导入或设置 `PYTHONPATH` 环境变量

### 5. 平台差异

- **Windows vs Linux/Mac**：注意路径、环境变量名称的差异
- **使用 `sys.platform`**：根据平台执行不同的代码逻辑

---

## 快速参考

### os 模块常用函数

| 函数 | 说明 |
|------|------|
| `os.getcwd()` | 获取当前工作目录 |
| `os.chdir(path)` | 改变工作目录 |
| `os.path.join(*paths)` | 路径拼接 |
| `os.path.exists(path)` | 检查路径是否存在 |
| `os.path.isfile(path)` | 检查是否为文件 |
| `os.path.isdir(path)` | 检查是否为目录 |
| `os.makedirs(path)` | 创建多级目录 |
| `os.listdir(path)` | 列出目录内容 |
| `os.walk(path)` | 递归遍历目录树 |
| `os.environ` | 环境变量字典 |
| `os.getpid()` | 获取进程 ID |

### sys 模块常用属性

| 属性/函数 | 说明 |
|----------|------|
| `sys.argv` | 命令行参数列表 |
| `sys.path` | Python 模块搜索路径 |
| `sys.platform` | 操作系统平台标识 |
| `sys.version` | Python 版本信息 |
| `sys.version_info` | Python 版本信息元组 |
| `sys.exit(code)` | 退出程序 |
| `sys.stdout` | 标准输出流 |
| `sys.stderr` | 标准错误流 |
| `sys.stdin` | 标准输入流 |
| `sys.modules` | 已导入模块字典 |

---

## 总结

`os` 和 `sys` 模块是 Python 系统编程的基础，掌握它们对于：

- ✅ 文件系统操作
- ✅ 路径处理
- ✅ 环境配置
- ✅ 命令行工具开发
- ✅ 跨平台兼容性

都非常重要。在实际项目中，经常需要结合使用这两个模块来实现复杂的系统交互功能。

