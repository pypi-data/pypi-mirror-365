#!/usr/bin/env python3
"""
Template Search MCP Server - HTTP 部署版本
支持 Streamable HTTP transport，可单独部署
"""

import json
import logging
import requests
import os

# MCP 1.9.4 的正确导入
from mcp.server.fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("template-mcp-server-http")

# 创建 MCP Server 实例 - 重要：启用 stateless_http
mcp = FastMCP("template-search-server")

# API 配置
TEMPLATE_API_BASE = "https://www.epub360.com"
SEARCH_ENDPOINT = f"{TEMPLATE_API_BASE}/templates/search.json"


@mcp.tool()
def search_templates(query: str, limit: int = 10) -> str:
    """
    根据关键词搜索 epub360 模板

    Args:
        query: 搜索关键词，例如：商务、教育、科技等
        limit: 返回结果数量限制，默认10个，最多50个

    Returns:
        JSON 格式的搜索结果
    """
    try:
        logger.info(f"HTTP 请求 - 搜索模板: {query}, 限制: {limit}")

        params = {
            "q": query.lower(),
            "limit": min(limit, 50)  # 限制最大50个
        }

        response = requests.get(
            SEARCH_ENDPOINT,
            params=params,
            timeout=10
        )
        response.raise_for_status()

        json_data = response.json()
        raw_results = json_data.get("data", [])

        # 格式化结果
        templates = []
        for item in raw_results:
            template = {
                "name": item.get("title", "未知标题"),
                "slug": item.get("slug", ""),
                "description": item.get("description", "无描述"),
                "cover": item.get("cover", ""),
            }
            templates.append(template)

        result = {
            "success": True,
            "query": query,
            "total": len(templates),
            "templates": templates
        }

        logger.info(f"HTTP 响应 - 找到 {len(templates)} 个模板")
        return json.dumps(result, ensure_ascii=False, indent=2)

    except requests.exceptions.RequestException as e:
        logger.error(f"API 请求错误: {e}")
        error_result = {
            "success": False,
            "query": query,
            "error": f"搜索请求失败: {str(e)}",
            "templates": []
        }
        return json.dumps(error_result, ensure_ascii=False)

    except Exception as e:
        logger.error(f"搜索错误: {e}")
        error_result = {
            "success": False,
            "query": query,
            "error": f"搜索过程中发生错误: {str(e)}",
            "templates": []
        }
        return json.dumps(error_result, ensure_ascii=False)


def main():
    """主函数 - 启动MCP服务器"""
    try:
        logger.info("启动 epub-mcp-server...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("HTTP 服务器已停止")
    except Exception as e:
        logger.error(f"HTTP 服务器启动失败: {e}")
        exit(1)


if __name__ == "__main__":
    main()