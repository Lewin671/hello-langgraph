from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# 创建 agent
agent = create_react_agent(
    model="ollama:qwen3:8b",
    tools=[get_weather],
    prompt="You are a helpful assistant."
)

# 初始化输入消息
input_messages = [{"role": "user", "content": "What's the weather in sf today?"}]

# 记录已输出的消息数量
seen = 0

# 流式运行 agent
for chunk in agent.stream({"messages": input_messages}, stream_mode="updates"):
    for node_name, node_data in chunk.items():
        if 'messages' in node_data:
            for message in node_data['messages']:
                # 处理对话内容
                isToolMessage = hasattr(message, 'name') and message.name
                if hasattr(message, 'content') and message.content:
                    # 过滤掉<think>标签内容
                    content = message.content
                    if '<think>' in content:
                        # 提取 <think> 和 </think> 之间的内容
                        thinking = content.split('<think>')[-1].split('</think>')[0].strip()
                        if thinking:
                            print(f"🤔 思考中: {thinking}")
                        # 提取</think>之后的内容
                        content = content.split('</think>')[-1].strip()
                    if content and not isToolMessage:
                        print(f"💬 [{node_name}]: {content}")
                
                # 处理工具调用
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        print(f"🔧 工具调用: {tool_call['name']}({tool_call['args']})")
                
                # 处理工具结果
                if isToolMessage:
                    print(f"✅ 工具结果 [{message.name}]: {message.content}")
