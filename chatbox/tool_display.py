"""
工具调用显示组件
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List
from config import load_config, load_theme

config = load_config()
theme = load_theme()


class ToolDisplay:
    """工具调用显示组件"""

    def __init__(self):
        self.active_tools = {}  # 正在执行的工具
        self.completed_tools = []  # 已完成的工具

    def start_tool(self, tool_name: str, tool_id: str, args: Dict[str, Any]):
        """开始工具调用"""
        self.active_tools[tool_id] = {
            "name": tool_name,
            "args": args,
            "start_time": time.time(),
            "status": "running",
        }
        self._print_tool_start(tool_id)

    def complete_tool(self, tool_id: str, result: Any):
        """完成工具调用"""
        if tool_id in self.active_tools:
            tool_info = self.active_tools[tool_id]
            tool_info["end_time"] = time.time()
            tool_info["duration"] = tool_info["end_time"] - tool_info["start_time"]
            tool_info["result"] = result
            tool_info["status"] = "completed"

            self.completed_tools.append(tool_info)
            del self.active_tools[tool_id]

            self._print_tool_complete(tool_id, tool_info)

    def _print_tool_start(self, tool_id: str):
        """打印工具开始信息"""
        tool_info = self.active_tools[tool_id]
        print(
            f"\n{theme.info}🔧 开始执行工具: {theme.bold}{tool_info['name']}{theme.reset}"
        )

        if config.show_tool_details and tool_info["args"]:
            args_str = json.dumps(tool_info["args"], ensure_ascii=False, indent=2)
            if len(args_str) > config.max_tool_args_length:
                args_str = args_str[: config.max_tool_args_length] + "..."
            print(f"{theme.muted}参数: {args_str}{theme.reset}")

    def _print_tool_complete(self, tool_id: str, tool_info: Dict[str, Any]):
        """打印工具完成信息"""
        print(
            f"\n{theme.success}✅ 工具执行完成: {theme.bold}{tool_info['name']}{theme.reset}"
        )
        print(f"{theme.muted}耗时: {tool_info['duration']:.2f}秒{theme.reset}")

        if config.show_tool_details:
            result_str = self._format_result(tool_info["result"])
            if len(result_str) > config.max_tool_result_length:
                result_str = result_str[: config.max_tool_result_length] + "..."
            print(f"{theme.secondary}结果: {result_str}{theme.reset}")

    def _format_result(self, result: Any) -> str:
        """格式化结果"""
        try:
            if isinstance(result, str):
                # 尝试解析JSON
                parsed = json.loads(result)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            else:
                return str(result)
        except:
            return str(result)

    def print_summary(self):
        """打印工具调用总结"""
        if not self.completed_tools:
            return

        total_time = sum(tool["duration"] for tool in self.completed_tools)
        avg_time = total_time / len(self.completed_tools)

        print(f"\n{theme.info}📊 工具调用总结:{theme.reset}")
        print(f"{theme.muted}   调用次数: {len(self.completed_tools)}")
        print(f"   总耗时: {total_time:.2f}秒")
        print(f"   平均耗时: {avg_time:.2f}秒/次")

        # 按工具类型分组统计
        tool_stats = {}
        for tool in self.completed_tools:
            name = tool["name"]
            if name not in tool_stats:
                tool_stats[name] = {"count": 0, "total_time": 0}
            tool_stats[name]["count"] += 1
            tool_stats[name]["total_time"] += tool["duration"]

        print(f"   工具详情:")
        for name, stats in tool_stats.items():
            avg = stats["total_time"] / stats["count"]
            print(f"     • {name}: {stats['count']}次, 平均{avg:.2f}秒/次")

        print(f"{theme.reset}")

    def clear(self):
        """清除所有工具信息"""
        self.active_tools.clear()
        self.completed_tools.clear()


class ProgressBar:
    """进度条组件"""

    def __init__(self, total: int, description: str = ""):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()

    def update(self, increment: int = 1):
        """更新进度"""
        self.current += increment
        self._print_progress()

    def _print_progress(self):
        """打印进度条"""
        if not config.show_progress:
            return

        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        percentage = self.current / self.total * 100

        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"

        print(
            f"\r{theme.secondary}{self.description} [{bar}] {percentage:.1f}% ({self.current}/{self.total}) {eta_str}{theme.reset}",
            end="",
            flush=True,
        )

    def complete(self):
        """完成进度条"""
        if config.show_progress:
            print()  # 换行


class StatusIndicator:
    """状态指示器"""

    def __init__(self):
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_char = 0

    def spin(self, message: str = ""):
        """显示旋转指示器"""
        char = self.spinner_chars[self.current_char]
        self.current_char = (self.current_char + 1) % len(self.spinner_chars)
        print(f"\r{theme.warning}{char} {message}{theme.reset}", end="", flush=True)

    def clear(self):
        """清除状态指示器"""
        print("\r" + " " * 80 + "\r", end="", flush=True)
