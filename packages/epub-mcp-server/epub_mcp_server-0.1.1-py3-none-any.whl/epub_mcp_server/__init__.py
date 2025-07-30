"""
epub-mcp-server - 智能模板发现助手

为 AI 应用提供强大的 epub360 模板搜索能力，通过 Model Context Protocol (MCP) 标准
为 Cursor、Claude 等 AI 工具提供强大的模板检索能力。
"""

__version__ = "0.1.1"
__author__ = "zhulinyi"
__email__ = "536555895@qq.com"

from .server import main

__all__ = ["main"]