# LangGraph CLI 对话系统

一个基于 LangGraph 的智能对话系统，支持工具调用和流式响应。

## 功能特性

### 🎨 优化的用户界面
- **彩色输出**: 支持彩色终端输出，提升用户体验
- **时间戳**: 显示消息发送时间
- **进度指示**: 实时显示工具调用进度
- **格式化显示**: 自动格式化JSON和复杂数据结构

### 🔧 工具调用优化
- **详细工具信息**: 显示工具名称、参数和结果
- **执行时间统计**: 显示每个工具的执行时间
- **调用总结**: 提供工具调用的统计信息
- **参数截断**: 自动截断过长的参数和结果

### 📊 交互功能
- **对话历史**: 查看最近的对话记录
- **工具列表**: 显示所有可用工具
- **保存对话**: 将对话保存到文件
- **清屏功能**: 清除屏幕重新开始

## 配置选项

### 环境变量配置

你可以通过环境变量来自定义CLI的行为：

```bash
# 禁用颜色输出
export CHATBOX_NO_COLORS=1

# 禁用时间戳显示
export CHATBOX_NO_TIMESTAMPS=1

# 禁用工具调用详情
export CHATBOX_NO_TOOL_DETAILS=1

# 禁用进度条
export CHATBOX_NO_PROGRESS=1

# 禁用工具调用总结
export CHATBOX_NO_TOOL_SUMMARY=1
```

### 配置文件

在 `config.py` 中可以修改默认配置：

```python
@dataclass
class UIConfig:
    enable_colors: bool = True
    show_timestamps: bool = True
    show_tool_details: bool = True
    show_progress: bool = True
    show_tool_summary: bool = True
    max_tool_args_length: int = 200
    max_tool_result_length: int = 500
    history_display_count: int = 10
```

## 使用方法

### 基本使用

```bash
cd chatbox
python chatbox.py
```

### 特殊命令

在对话过程中，你可以使用以下特殊命令：

- `help` - 显示帮助信息
- `clear` - 清屏
- `tools` - 显示可用工具列表
- `history` - 显示对话历史
- `save <filename>` - 保存对话到文件
- `quit` / `exit` / `退出` - 退出对话

### 示例对话

```
👤 你: 使用sequential thinking工具告诉我如何成为百万富翁？

🤖 助手: 
🔧 开始执行工具: sequentialthinking
参数: {
  "thought": "To become a millionaire, one must first understand the foundational principles of wealth accumulation...",
  "nextThoughtNeeded": true,
  "thoughtNumber": 1,
  "totalThoughts": 5
}

✅ 工具执行完成: sequentialthinking
耗时: 1.23秒
结果: {
  "thoughtNumber": 1,
  "totalThoughts": 5,
  "nextThoughtNeeded": true
}

📊 工具调用总结:
   调用次数: 5
   总耗时: 6.15秒
   平均耗时: 1.23秒/次
   工具详情:
     • sequentialthinking: 5次, 平均1.23秒/次

Here's a step-by-step guide to becoming a millionaire...
```

## 技术架构

### 组件结构

```
chatbox/
├── chatbox.py          # 主程序
├── config.py           # 配置管理
├── tool_display.py     # 工具显示组件
└── README.md          # 说明文档
```

### 核心组件

1. **UI类**: 提供统一的用户界面输出
2. **ToolDisplay类**: 专门处理工具调用的显示
3. **ProgressBar类**: 进度条显示
4. **StatusIndicator类**: 状态指示器

### 主题系统

支持自定义主题颜色：

```python
class Theme:
    primary: str = "\033[94m"    # 蓝色
    secondary: str = "\033[96m"  # 青色
    success: str = "\033[92m"    # 绿色
    warning: str = "\033[93m"    # 黄色
    error: str = "\033[91m"      # 红色
    info: str = "\033[95m"       # 紫色
    muted: str = "\033[90m"      # 灰色
```

## 故障排除

### 常见问题

1. **颜色不显示**: 检查终端是否支持ANSI颜色，或设置 `CHATBOX_NO_COLORS=1`
2. **工具调用信息过多**: 设置 `CHATBOX_NO_TOOL_DETAILS=1` 或调整 `max_tool_args_length`
3. **性能问题**: 禁用进度条和工具总结可以提升性能

### 调试模式

可以通过修改配置文件来启用调试模式，显示更多详细信息。

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！ 