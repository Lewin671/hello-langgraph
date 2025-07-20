# LangGraph CLI 对话系统

这是一个基于 LangGraph 的命令行对话系统，支持多轮对话和工具调用。

## 功能特性

- 🤖 交互式命令行对话
- 🔧 支持工具调用（天气查询、数学计算）
- 💭 显示AI思考过程
- 📝 多轮对话历史保持
- 🚀 流式响应输出

## 使用方法

### 方法1：直接运行
```bash
cd src/chatbox
python chatbox.py
```

### 方法2：使用启动脚本
```bash
cd src/chatbox
python run_chat.py
```

### 方法3：从项目根目录运行
```bash
python src/chatbox/chatbox.py
```

## 对话示例

```
🤖 欢迎使用 LangGraph CLI 对话系统!
💡 输入 'quit' 或 'exit' 退出对话
==================================================

👤 你: 今天天气怎么样？

🤖 助手: 🤔 思考中: 用户询问天气，我需要使用天气工具来获取信息
🔧 工具调用: get_weather({'city': 'today'})
✅ 工具结果 [get_weather]: It's always sunny in today!
💬 [agent]: 根据天气查询结果，今天天气很好，阳光明媚！

👤 你: 帮我查询北京的天气

🤖 助手: 🤔 思考中: 用户想要查询北京的天气，我需要使用天气工具
🔧 工具调用: get_weather({'city': '北京'})
✅ 工具结果 [get_weather]: It's always sunny in 北京!
💬 [agent]: 北京的天气很好，阳光明媚！

👤 你: 计算 15 * 8 + 20

🤖 助手: 🤔 思考中: 用户需要计算数学表达式，我应该使用计算器工具
🔧 工具调用: calculator({'expression': '15 * 8 + 20'})
✅ 工具结果 [calculator]: The result of 15 * 8 + 20 is 140
💬 [agent]: 计算结果：15 * 8 + 20 = 140

👤 你: exit

👋 再见!
```

## 退出对话

输入以下任一命令可以退出对话：
- `quit`
- `exit` 
- `退出`

或者按 `Ctrl+C` 强制退出。

## 配置说明

当前系统使用以下配置：
- **模型**: Ollama Granite 3.3 8B
- **工具**: 天气查询工具、数学计算器
- **提示词**: "You are a helpful assistant."

## 自定义

你可以通过修改 `chatbox.py` 文件来自定义：

1. **添加新工具**: 在 `get_weather` 和 `calculator` 函数附近添加新的工具函数
2. **更换模型**: 修改 `create_react_agent` 中的 `model` 参数
3. **修改提示词**: 更改 `prompt` 参数
4. **调整输出格式**: 修改 `process_stream_response` 函数中的输出逻辑

## 依赖要求

确保已安装以下依赖：
- langgraph[langchain]
- langchain
- langchain-ollama

如果使用 Ollama 模型，请确保本地已安装并运行 Ollama 服务。 