from ast import mod
import asyncio
import json
import time
from datetime import datetime
from langchain_ollama.chat_models import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
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
from config import load_config, load_theme
from tool_display import ToolDisplay, ProgressBar, StatusIndicator

# 加载配置和主题
config = load_config()
theme = load_theme()


# 颜色代码
class Colors:
    RESET = theme.reset
    BOLD = theme.bold
    RED = theme.error
    GREEN = theme.success
    YELLOW = theme.warning
    BLUE = theme.primary
    MAGENTA = theme.info
    CYAN = theme.secondary
    WHITE = "\033[97m"
    GRAY = theme.muted


# UI 组件
class UI:
    @staticmethod
    def print_header():
        """打印欢迎头部"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    🤖 LangGraph CLI 对话系统                  ║")
        print("║                    智能助手 + 工具调用                        ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")
        print(f"{Colors.GRAY}💡 输入 'quit' 或 'exit' 退出对话")
        print(f"💡 输入 'help' 查看帮助信息")
        print(f"{Colors.RESET}")
        print("=" * 60)

    @staticmethod
    def print_user_input(text):
        """打印用户输入"""
        if config.show_timestamps:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"\n{Colors.BLUE}{Colors.BOLD}👤 你 [{timestamp}]:{Colors.RESET} {text}"
            )
        else:
            print(f"\n{Colors.BLUE}{Colors.BOLD}👤 你:{Colors.RESET} {text}")

    @staticmethod
    def print_assistant_start():
        """打印助手开始回复"""
        if config.show_timestamps:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}🤖 助手 [{timestamp}]:{Colors.RESET} ",
                end="",
                flush=True,
            )
        else:
            print(
                f"\n{Colors.GREEN}{Colors.BOLD}🤖 助手:{Colors.RESET} ",
                end="",
                flush=True,
            )

    @staticmethod
    def print_thinking(thought):
        """打印思考过程"""
        print(f"\n{Colors.YELLOW}🤔 思考中: {thought}{Colors.RESET}")

    @staticmethod
    def print_tool_call(tool_name, args):
        """打印工具调用"""
        if not config.show_tool_details:
            return

        print(f"\n{Colors.MAGENTA}🔧 工具调用: {Colors.BOLD}{tool_name}{Colors.RESET}")
        if args:
            # 格式化参数显示
            args_str = json.dumps(args, ensure_ascii=False, indent=2)
            if len(args_str) > config.max_tool_args_length:
                args_str = args_str[: config.max_tool_args_length] + "..."
            print(f"{Colors.GRAY}参数: {args_str}{Colors.RESET}")

    @staticmethod
    def print_tool_result(tool_name, result):
        """打印工具结果"""
        if not config.show_tool_details:
            return

        print(f"\n{Colors.GREEN}✅ 工具结果 [{tool_name}]:{Colors.RESET}")
        # 尝试解析JSON结果并格式化显示
        try:
            if isinstance(result, str):
                parsed = json.loads(result)
                result_str = json.dumps(parsed, ensure_ascii=False, indent=2)
            else:
                result_str = str(result)

            if len(result_str) > config.max_tool_result_length:
                result_str = result_str[: config.max_tool_result_length] + "..."
            print(f"{Colors.CYAN}{result_str}{Colors.RESET}")
        except:
            result_str = str(result)
            if len(result_str) > config.max_tool_result_length:
                result_str = result_str[: config.max_tool_result_length] + "..."
            print(f"{Colors.CYAN}{result_str}{Colors.RESET}")

    @staticmethod
    def print_content(content, node_name=""):
        """打印内容"""
        if node_name:
            print(f"{Colors.GREEN}💬 [{node_name}]:{Colors.RESET} {content}")
        else:
            print(content, end="", flush=True)

    @staticmethod
    def print_error(error):
        """打印错误信息"""
        print(f"\n{Colors.RED}❌ 错误: {error}{Colors.RESET}")

    @staticmethod
    def print_success(message):
        """打印成功信息"""
        print(f"\n{Colors.GREEN}✅ {message}{Colors.RESET}")

    @staticmethod
    def print_info(message):
        """打印信息"""
        print(f"\n{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

    @staticmethod
    def print_progress(current, total, description=""):
        """打印进度条"""
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        percentage = current / total * 100
        print(
            f"\r{Colors.CYAN}{description} [{bar}] {percentage:.1f}% ({current}/{total}){Colors.RESET}",
            end="",
            flush=True,
        )

    @staticmethod
    def clear_progress():
        """清除进度条"""
        print("\r" + " " * 80 + "\r", end="", flush=True)

    @staticmethod
    def print_tool_summary(tool_calls, total_time):
        """打印工具调用总结"""
        if not config.show_tool_summary or not tool_calls:
            return

        print(f"\n{Colors.MAGENTA}📊 工具调用总结:{Colors.RESET}")
        print(f"{Colors.GRAY}   调用次数: {len(tool_calls)}")
        print(f"   总耗时: {total_time:.2f}秒")
        if len(tool_calls) > 0:
            print(f"   平均耗时: {total_time/len(tool_calls):.2f}秒/次")
        print(
            f"   工具列表: {', '.join([tc['name'] for tc in tool_calls])}{Colors.RESET}"
        )

    @staticmethod
    def print_help():
        """打印帮助信息"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}📖 帮助信息:{Colors.RESET}")
        print(f"{Colors.GRAY}• quit/exit/退出 - 退出对话")
        print(f"• help - 显示此帮助信息")
        print(f"• clear - 清屏")
        print(f"• tools - 显示可用工具列表")
        print(f"• history - 显示对话历史")
        print(f"• save <filename> - 保存对话历史到文件{Colors.RESET}")


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a specific city.

    Use this tool when the user asks about weather conditions in any city.

    Args:
        city: The name of the city to get weather for (e.g., "Beijing", "San Francisco")

    Returns:
        A string describing the current weather in the specified city
    """
    return f"It's always sunny in {city}!"


def loadMCPConfig():
    # 从项目根目录下加载 mcp.json
    with open(Path(__file__).parent.parent / "mcp.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def process_stream_response(agent, messages):
    """处理流式响应并返回所有新消息"""
    new_messages = []
    tool_display = ToolDisplay()
    start_time = time.time()

    async for chunk in agent.astream({"messages": messages}, stream_mode="updates"):
        for node_name, node_data in chunk.items():
            if "messages" in node_data:
                for message in node_data["messages"]:
                    # 添加消息到新消息列表
                    new_messages.append(message)

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
                                UI.print_thinking(thinking)
                            # 提取</think>之后的内容
                            content = content.split("</think>")[-1].strip()
                        if content and not isToolMessage:
                            UI.print_content(content, node_name)

                    # 处理工具调用
                    if hasattr(message, "tool_calls") and message.tool_calls:
                        for tool_call in message.tool_calls:
                            tool_id = tool_display.start_tool(
                                tool_call["name"], tool_call["args"]
                            )

                    # 处理工具结果
                    if isToolMessage:
                        # 找到对应的工具调用并完成
                        for tool_id, tool_info in tool_display.active_tools.items():
                            if tool_info["name"] == message.name:
                                tool_display.complete_tool(tool_id, message.content)
                                break

    total_time = time.time() - start_time
    tool_display.print_summary()

    return new_messages


async def main():
    """主对话循环"""
    UI.print_header()

    # 创建 agent
    try:
        UI.print_info("正在初始化模型和工具...")
        llm = create_llm()
        tools, cleanup = await convert_mcp_to_langchain_tools(
            loadMCPConfig()["mcpServers"]
        )

        UI.print_success(f"初始化完成! 可用工具数量: {len(tools) + 1}")

        agent = create_react_agent(
            model=llm,
            tools=[get_weather, *tools],
            prompt="""You are a helpful assistant with access to tools. """,
        )

        # 初始化对话历史
        messages = []
        conversation_start = datetime.now()

        while True:
            try:
                # 获取用户输入
                user_input = input(f"\n{Colors.BLUE}👤 你: {Colors.RESET}").strip()

                # 检查特殊命令
                if user_input.lower() in ["quit", "exit", "退出"]:
                    UI.print_success("再见!")
                    break
                elif user_input.lower() == "help":
                    UI.print_help()
                    continue
                elif user_input.lower() == "clear":
                    os.system("clear" if os.name == "posix" else "cls")
                    UI.print_header()
                    continue
                elif user_input.lower() == "tools":
                    UI.print_info("可用工具:")
                    for i, tool in enumerate([get_weather, *tools], 1):
                        print(
                            f"{Colors.GRAY}  {i}. {tool.name}: {tool.description}{Colors.RESET}"
                        )
                    continue
                elif user_input.lower() == "history":
                    UI.print_info(f"对话历史 (共 {len(messages)} 条消息):")
                    for i, msg in enumerate(
                        messages[-config.history_display_count :], 1
                    ):  # 只显示最近N条
                        if isinstance(msg, HumanMessage):
                            print(
                                f"{Colors.GRAY}  {i}. 👤 你: {msg.content[:50]}...{Colors.RESET}"
                            )
                        elif isinstance(msg, ToolMessage):
                            print(
                                f"{Colors.GRAY}  {i}. 🔧 工具 [{msg.name}]: {msg.content[:50]}...{Colors.RESET}"
                            )
                        elif isinstance(msg, AIMessage):
                            content = msg.content or ""
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                tool_names = [
                                    tc.get("name", "unknown") for tc in msg.tool_calls
                                ]
                                print(
                                    f"{Colors.GRAY}  {i}. 🤖 助手: {content[:30]}... [调用工具: {', '.join(tool_names)}]{Colors.RESET}"
                                )
                            else:
                                print(
                                    f"{Colors.GRAY}  {i}. 🤖 助手: {content[:50]}...{Colors.RESET}"
                                )
                        else:
                            print(
                                f"{Colors.GRAY}  {i}. 🤖 助手: {msg.content[:50]}...{Colors.RESET}"
                            )
                    continue
                elif user_input.lower().startswith("save "):
                    filename = user_input[5:].strip()
                    if filename:
                        try:
                            with open(filename, "w", encoding="utf-8") as f:
                                f.write(
                                    f"对话记录 - {conversation_start.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                )
                                f.write("=" * 50 + "\n\n")
                                for msg in messages:
                                    if isinstance(msg, HumanMessage):
                                        f.write(f"👤 你: {msg.content}\n\n")
                                    elif isinstance(msg, ToolMessage):
                                        f.write(
                                            f"🔧 工具 [{msg.name}]: {msg.content}\n\n"
                                        )
                                    elif isinstance(msg, AIMessage):
                                        # 处理AI消息，包括工具调用
                                        content = msg.content or ""
                                        if (
                                            hasattr(msg, "tool_calls")
                                            and msg.tool_calls
                                        ):
                                            f.write(f"🤖 助手: {content}\n")
                                            for tool_call in msg.tool_calls:
                                                tool_name = tool_call.get(
                                                    "name", "unknown"
                                                )
                                                tool_args = tool_call.get("args", {})
                                                args_str = json.dumps(
                                                    tool_args,
                                                    ensure_ascii=False,
                                                    indent=2,
                                                )
                                                f.write(f"🔧 调用工具 [{tool_name}]:\n")
                                                f.write(f"   参数: {args_str}\n\n")
                                        else:
                                            f.write(f"🤖 助手: {content}\n\n")
                                    else:
                                        f.write(f"🤖 助手: {msg.content}\n\n")
                            UI.print_success(f"对话已保存到 {filename}")
                        except Exception as e:
                            UI.print_error(f"保存失败: {e}")
                    continue

                # 跳过空输入
                if not user_input:
                    continue

                # 添加用户消息到历史
                messages.append(HumanMessage(content=user_input))
                UI.print_user_input(user_input)

                UI.print_assistant_start()

                # 处理AI响应
                new_messages = await process_stream_response(agent, messages)

                # 添加所有新消息到历史
                messages.extend(new_messages)

                print()  # 换行

            except KeyboardInterrupt:
                print("\n")
                UI.print_success("再见!")
                break
            except Exception as e:
                UI.print_error(f"发生错误: {e}")
                continue

        await cleanup()

    except Exception as e:
        UI.print_error(f"初始化失败: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
