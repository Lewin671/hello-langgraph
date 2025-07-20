# LLM Factory

这个模块提供了一个 LLM 工厂类，用于从 `.env` 文件读取配置并创建相应的语言模型实例。

## 功能特性

- 支持 OpenAI 和 Ollama 模型
- 从 `.env` 文件自动读取配置
- 自动查找项目根目录
- 提供便捷的创建函数

## 配置选项

在项目根目录创建 `.env` 文件，包含以下配置：

```env
# 模型类型: "openai" 或 "ollama"
LLM_TYPE=openai

# 模型名称 (例如: "gpt-3.5-turbo", "gpt-4", "llama2" 等)
LLM_MODEL_NAME=gpt-3.5-turbo

# API Key (OpenAI 模型必需)
LLM_API_KEY=your_openai_api_key_here

# Base URL (可选，用于自定义端点)
LLM_BASE_URL=https://api.openai.com/v1
```

## 使用方法

### 基本用法

```python
from common.llm_factory import create_llm

# 创建 LLM 实例
llm = create_llm()

# 使用 LLM
response = llm.invoke("Hello, world!")
```

### 高级用法

```python
from common.llm_factory import LLMFactory

# 创建工厂实例
factory = LLMFactory()

# 查看当前配置
config = factory.get_config()
print(config)

# 创建 LLM 实例并传递额外参数
llm = factory.create_llm(temperature=0.7, max_tokens=1000)
```

### 配置示例

#### OpenAI 模型
```env
LLM_TYPE=openai
LLM_MODEL_NAME=gpt-4
LLM_API_KEY=sk-your-api-key
LLM_BASE_URL=https://api.openai.com/v1
```

#### Ollama 模型
```env
LLM_TYPE=ollama
LLM_MODEL_NAME=llama2
LLM_BASE_URL=http://localhost:11434
```

#### Azure OpenAI
```env
LLM_TYPE=openai
LLM_MODEL_NAME=gpt-35-turbo
LLM_API_KEY=your-azure-api-key
LLM_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/your-deployment
```

## 依赖项

确保安装了以下依赖：

```bash
poetry add python-dotenv langchain-openai
```

## 错误处理

- 如果 `.env` 文件不存在，会使用系统环境变量
- 如果缺少必需的配置（如 API Key），会抛出 `ValueError`
- 如果模型类型不支持，会抛出 `ValueError` 