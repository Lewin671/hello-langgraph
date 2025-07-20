"""
CLI 配置文件
"""

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class UIConfig:
    """UI配置"""

    # 是否启用颜色
    enable_colors: bool = True
    # 是否显示时间戳
    show_timestamps: bool = True
    # 是否显示工具调用详情
    show_tool_details: bool = True
    # 是否显示进度条
    show_progress: bool = True
    # 是否显示工具调用总结
    show_tool_summary: bool = True
    # 最大显示的工具参数长度
    max_tool_args_length: int = 200
    # 最大显示的工具结果长度
    max_tool_result_length: int = 500
    # 历史记录显示条数
    history_display_count: int = 10


@dataclass
class Theme:
    """主题配置"""

    # 主色调
    primary: str = "\033[94m"  # 蓝色
    secondary: str = "\033[96m"  # 青色
    success: str = "\033[92m"  # 绿色
    warning: str = "\033[93m"  # 黄色
    error: str = "\033[91m"  # 红色
    info: str = "\033[95m"  # 紫色
    muted: str = "\033[90m"  # 灰色
    reset: str = "\033[0m"
    bold: str = "\033[1m"


# 默认配置
DEFAULT_CONFIG = UIConfig()
DEFAULT_THEME = Theme()


# 从环境变量加载配置
def load_config() -> UIConfig:
    """从环境变量加载配置"""
    config = UIConfig()

    # 从环境变量读取配置
    if os.getenv("CHATBOX_NO_COLORS"):
        config.enable_colors = False
    if os.getenv("CHATBOX_NO_TIMESTAMPS"):
        config.show_timestamps = False
    if os.getenv("CHATBOX_NO_TOOL_DETAILS"):
        config.show_tool_details = False
    if os.getenv("CHATBOX_NO_PROGRESS"):
        config.show_progress = False
    if os.getenv("CHATBOX_NO_TOOL_SUMMARY"):
        config.show_tool_summary = False

    return config


def load_theme() -> Theme:
    """加载主题"""
    return DEFAULT_THEME
