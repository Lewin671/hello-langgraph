# 故障排除指南

## 常见问题

### 1. AI没有调用工具

**症状**: AI直接回答问题而不调用工具

**可能原因**:
- 模型不支持工具调用
- 工具定义不正确
- 提示词不够明确

**解决方案**:
1. 确保使用支持工具调用的模型
2. 检查工具是否正确使用 `@tool` 装饰器
3. 使用更明确的提示词

### 2. 模型响应缓慢或无响应

**症状**: 程序卡住或响应很慢

**可能原因**:
- Ollama服务未运行
- 模型未下载
- 网络连接问题

**解决方案**:
```bash
# 检查Ollama状态
ollama list

# 启动Ollama服务
ollama serve

# 拉取模型
ollama pull granite3.3:8b
```

### 3. 工具调用失败

**症状**: 看到工具调用但结果错误

**可能原因**:
- 工具函数有错误
- 参数类型不匹配
- 权限问题

**解决方案**:
1. 检查工具函数的实现
2. 确保参数类型正确
3. 添加错误处理

## 调试步骤

### 步骤1: 检查基础连接
```bash
python -c "from langchain_ollama import OllamaLLM; llm = OllamaLLM(model='granite3.3:8b'); print(llm.invoke('Hello'))"
```

### 步骤2: 测试工具定义
```bash
python -c "from chatbox import get_weather, calculator; print(get_weather('Beijing')); print(calculator('2+2'))"
```

### 步骤3: 测试完整对话
```bash
python chatbox.py
```

## 模型建议

如果当前模型不支持工具调用，可以尝试：

1. **使用其他Ollama模型**:
   ```bash
   ollama pull llama3.2:3b
   ollama pull qwen2.5:7b
   ```

2. **修改模型配置**:
   在 `chatbox.py` 中更改模型名称

## 日志和调试

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 联系支持

如果问题仍然存在，请检查：
1. Python版本 (需要 3.13+)
2. 依赖包版本
3. Ollama版本
4. 系统资源 (内存、CPU) 