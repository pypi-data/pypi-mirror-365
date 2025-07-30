# Pretty Build - 增强型构建系统包装器

一个功能强大的构建系统包装器，为 Ninja、Make 和 CMake 提供美观的实时界面、性能监控、智能缓存和插件系统。

## ✨ 主要功能

### 🎨 美观的用户界面
- 响应式网格布局，自适应终端大小
- 实时进度显示和构建状态
- 彩色输出和错误高亮
- 内存使用情况可视化

### ⚡ 性能优化
- 智能构建缓存系统
- 实时性能监控
- 并行构建支持
- 增量构建检测

### 🔌 插件系统
- 可扩展的插件架构
- 内置日志插件
- 自定义构建流程钩子
- 消息处理管道

### 🔔 通知系统
- 跨平台系统通知
- 构建完成提醒
- 错误和警告通知
- 可配置的通知设置

### ⌨️ 交互式控制
- 实时键盘快捷键
- 暂停/恢复构建
- 动态配置调整
- 性能监控界面

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 基本使用
```bash
# 自动检测构建系统并构建
python pretty_build.py

# 指定构建系统
python pretty_build.py --build-system ninja

# 清理构建
python pretty_build.py --clean

# 重新构建
python pretty_build.py --rebuild

# 设置并行任务数
python pretty_build.py --jobs 8

# 启用详细输出
python pretty_build.py --verbose
```

## ⌨️ 键盘快捷键

在构建过程中，您可以使用以下快捷键：

| 快捷键 | 功能 |
|--------|------|
| `P` | 暂停/恢复构建 |
| `Q` | 退出构建 |
| `C` | 打开配置界面 |
| `H` | 显示帮助信息 |
| `F` | 性能监控界面 |
| `G` | 插件管理界面 |
| `X` | 缓存管理 |
| `N` | 通知设置 |

## 🔧 配置选项

### 命令行参数
```bash
python pretty_build.py --help
```

### 配置文件
程序会自动创建和使用 `.pretty_build.conf` 配置文件，包含以下选项：

- **构建设置**: 并行任务数、构建类型、优化级别
- **缓存设置**: 启用缓存、缓存目录、缓存大小限制
- **通知设置**: 系统通知、声音提醒
- **性能监控**: CPU/内存监控、性能报告
- **插件配置**: 启用的插件列表

## 🔌 插件开发

### 创建自定义插件
```python
from pretty_build import BuildPlugin, MessageType

class MyPlugin(BuildPlugin):
    def __init__(self):
        super().__init__("my_plugin", "1.0.0")
    
    def initialize(self, config, console):
        # 插件初始化逻辑
        return True
    
    def on_build_start(self, build_state):
        # 构建开始时的处理
        pass
    
    def on_build_end(self, build_state, return_code):
        # 构建结束时的处理
        pass
    
    def process_message(self, message, msg_type):
        # 处理构建消息
        return message
```

### 注册插件
```python
plugin_manager.register_plugin(MyPlugin())
```

## 📊 性能监控

实时监控以下指标：
- CPU 使用率
- 内存使用量
- 构建时间
- 编译文件数
- 错误和警告统计

## 🗂️ 智能缓存

- 基于文件哈希的智能缓存
- 自动检测文件变更
- 增量构建支持
- 缓存统计和管理

## 🔔 通知系统

支持以下通知类型：
- 构建成功/失败
- 错误和警告
- 性能警报
- 自定义通知

## 🛠️ 支持的构建系统

- **Ninja**: 快速并行构建
- **GNU Make**: 传统 Makefile 支持
- **CMake**: 跨平台构建系统

## 📋 系统要求

- Python 3.8+
- Windows/Linux/macOS
- 终端支持 ANSI 颜色

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🔗 相关链接

- [Rich 库文档](https://rich.readthedocs.io/)
- [Ninja 构建系统](https://ninja-build.org/)
- [CMake 文档](https://cmake.org/documentation/)