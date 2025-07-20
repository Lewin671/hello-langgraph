from ast import mod
import asyncio
import json
from langchain_ollama.chat_models import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_ollama import OllamaLLM
import sys
import os
from pathlib import Path
from langchain_mcp_tools import convert_mcp_to_langchain_tools

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from common.llm_factory import create_llm


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a specific city.

    Use this tool when the user asks about weather conditions in any city.

    Args:
        city: The name of the city to get weather for (e.g., "Beijing", "San Francisco")

    Returns:
        A string describing the current weather in the specified city
    """
    print(f"[tool-call]get_weather: {city}")
    return f"It's always sunny in {city}!"


def loadMCPConfig():
    # 从项目根目录下加载 mcp.json
    with open(Path(__file__).parent.parent / "mcp.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def process_stream_response(agent, messages):
    """处理流式响应并返回AI的回复"""
    ai_response = ""
    tool_was_called = False

    async for chunk in agent.astream({"messages": messages}, stream_mode="updates"):
        for node_name, node_data in chunk.items():
            if "messages" in node_data:
                for message in node_data["messages"]:
                    # 处理对话内容
                    isToolMessage = hasattr(message, "name") and message.name
                    if hasattr(message, "content") and message.content:
                        # 过滤掉<think>标签内容
                        content = message.content
                        if "<think>" in content:
                            # 提取 <think> 和 </think> 之间的内容
                            thinking = (
                                content.split("<think>")[-1]
                                .split("</think>")[0]
                                .strip()
                            )
                            if thinking:
                                print(f"🤔 思考中: {thinking}")
                            # 提取</think>之后的内容
                            content = content.split("</think>")[-1].strip()
                        if content and not isToolMessage:
                            print(f"💬 [{node_name}]: {content}")
                            ai_response += content

                    # 处理工具调用
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        tool_was_called = True
                        for tool_call in message.tool_calls:
                            print(
                                f"🔧 工具调用: {tool_call['name']}({tool_call['args']})"
                            )

                    # 处理工具结果
                    if isToolMessage:
                        tool_was_called = True
                        print(f"✅ 工具结果 [{message.name}]: {message.content}")

    return ai_response


async def main():
    """主对话循环"""
    print("🤖 欢迎使用 LangGraph CLI 对话系统!")
    print("💡 输入 'quit' 或 'exit' 退出对话")
    print("=" * 50)

    # 创建 agent
    llm = create_llm()
    tools, cleanup = await convert_mcp_to_langchain_tools(loadMCPConfig()["mcpServers"])

    print("mcp tools: ", tools)

    agent = create_react_agent(
        model=llm,
        tools=[get_weather, *tools],
        prompt="""You are a helpful assistant with access to tools. """,
    )

    # 初始化对话历史
    messages = []

    while True:
        try:
            # 获取用户输入
            user_input = input("\n👤 你: ").strip()

            # 检查退出命令
            if user_input.lower() in ["quit", "exit", "退出"]:
                print("👋 再见!")
                break

            # 跳过空输入
            if not user_input:
                continue

            # 添加用户消息到历史
            messages.append(HumanMessage(content=user_input))

            print("\n🤖 助手: ", end="", flush=True)

            # 处理AI响应
            ai_response = await process_stream_response(agent, messages)

            # 添加AI消息到历史
            if ai_response:
                messages.append(AIMessage(content=ai_response))

            print()  # 换行

        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            continue
    await cleanup()


if __name__ == "__main__":
    asyncio.run(main())
