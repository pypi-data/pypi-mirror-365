"""MCP Metaso服务器 - 使用官方FastMCP SDK实现

提供基于MCP协议的Metaso AI搜索引擎服务器功能，包括多维搜索和网页解析。
"""
import asyncio
import logging
import os
import sys
from typing import Any, Dict
import json

import httpx
import mcp
from mcp.server.fastmcp import FastMCP

from .config import config
from .formatters import (
    RESULT_FORMATTERS,
    SCOPE_RESULT_MAPPING,
    SCOPE_CN_MAPPING
)

# 设置日志 - 适配Claude Desktop环境
log_level = os.environ.get("MCP_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr  # Claude Desktop需要日志输出到stderr
)
logger = logging.getLogger(__name__)

# 降低第三方库的日志级别
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def create_server() -> FastMCP:
    """创建MCP服务器实例
    
    Returns:
        FastMCP: 配置好的MCP服务器实例
    """
    # 创建FastMCP服务器实例
    mcp_server = FastMCP("mcp-metaso")
    
    @mcp_server.tool()
    async def metaso_search(
        query: str, 
        scope: str = "webpage", 
        include_summary: bool = False, 
        size: int = 10
    ) -> str:
        """使用Metaso AI搜索引擎搜索信息
        
        Args:
            query: 搜索查询词
            scope: 搜索范围，支持：webpage（网页）、document（文库）、scholar（学术）、image（图片）、video（视频）、podcast（播客）
            include_summary: 是否包含摘要，默认False
            size: 返回结果数量，默认10，范围1-20
            
        Returns:
            str: 格式化的搜索结果
            
        Raises:
            Exception: 当搜索失败时抛出异常
        """
        try:
            # 验证scope参数
            if scope not in SCOPE_RESULT_MAPPING:
                supported_scopes = ", ".join(SCOPE_RESULT_MAPPING.keys())
                return f"错误: 不支持的搜索范围 '{scope}'。支持的范围: {supported_scopes}"
            
            # 验证size参数
            if not (1 <= size <= 20):
                return "错误: size参数必须在1-20之间"
            
            url = f"{config.base_url}/search"
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            data = {
                "q": query,
                "scope": scope,
                "includeSummary": include_summary,
                "size": str(size)
            }
            
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
            
            return _format_search_result(result, query, scope, include_summary)
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP请求错误: {e}")
            return f"搜索失败: HTTP错误 - {str(e)}"
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return f"搜索失败: {str(e)}"
    
    @mcp_server.tool()
    async def metaso_reader(url: str, output_format: str = "markdown") -> str:
        """解析网页内容并提取文本
        
        Args:
            url: 要解析的网页URL
            output_format: 输出格式，支持"markdown"（默认）或"json"
            
        Returns:
            str: 解析后的网页内容
            
        Raises:
            Exception: 当网页解析失败时抛出异常
        """
        try:
            # 验证output_format参数
            if output_format not in ["markdown", "json"]:
                return "错误: output_format参数必须是'markdown'或'json'"
            
            api_url = f"{config.base_url}/reader"
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "Accept": "text/plain" if output_format == "markdown" else "application/json"
            }
            data = {"url": url}
            
            async with httpx.AsyncClient(timeout=config.timeout) as client:
                response = await client.post(api_url, headers=headers, json=data)
                response.raise_for_status()
            
            if output_format == "markdown":
                content = response.text
            else:
                content = json.dumps(response.json(), ensure_ascii=False, indent=2)
            
            formatted_content = f"# 网页内容解析\n\n**URL**: {url}\n\n## 解析结果\n\n{content}"
            return formatted_content
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP请求错误: {e}")
            return f"网页解析失败: HTTP错误 - {str(e)}"
        except Exception as e:
            logger.error(f"网页解析失败: {e}")
            return f"网页解析失败: {str(e)}"
    
    return mcp_server


def _format_search_result(
    result: Dict[str, Any], 
    query: str, 
    scope: str, 
    include_summary: bool
) -> str:
    """格式化搜索结果
    
    Args:
        result: API返回的原始结果
        query: 搜索查询词
        scope: 搜索范围
        include_summary: 是否包含摘要
        
    Returns:
        str: 格式化后的搜索结果
    """
    formatted_result = f"# {SCOPE_CN_MAPPING[scope]}搜索结果：{query}\n\n"
    
    # 处理摘要
    if include_summary and result.get('summary'):
        formatted_result += f"## 搜索摘要\n{result['summary']}\n\n"
    
    # 获取对应scope的结果数据
    result_key = SCOPE_RESULT_MAPPING[scope]
    items = result.get(result_key, [])
    
    if not items:
        formatted_result += f"未找到相关{SCOPE_CN_MAPPING[scope]}结果。\n"
        return formatted_result
    
    # 使用对应的格式化函数
    formatter = RESULT_FORMATTERS[scope]
    for i, item in enumerate(items, 1):
        formatted_result += formatter(item, i)
    
    # 添加结果统计
    formatted_result += f"---\n**共找到 {len(items)} 条{SCOPE_CN_MAPPING[scope]}结果**"
    
    return formatted_result


def main() -> None:
    """主函数 - 启动MCP服务器
    
    启动MCP Metaso服务器，处理客户端连接和请求。
    """
    logger.info("启动MCP Metaso服务器...")
    logger.info(f"Python版本: {sys.version}")
    logger.info(f"MCP SDK版本: {mcp.__version__ if hasattr(mcp, '__version__') else 'unknown'}")
    
    # 检查API密钥
    if not config.api_key:
        logger.warning("警告: 未设置METASO_API_KEY环境变量")
        logger.warning("服务器将启动但搜索功能不可用")
        logger.warning("请在Claude Desktop配置中添加API密钥或设置环境变量:")
        logger.warning("export METASO_API_KEY='your_key_here'")
    else:
        logger.info("API密钥已配置，服务器功能完整")
    
    try:
        # 创建并启动服务器
        server = create_server()
        logger.info("MCP Metaso服务器启动成功，等待客户端连接...")
        server.run()
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务器...")
    except Exception as e:
        logger.error(f"服务器运行出错: {e}")
        raise


if __name__ == "__main__":
    main()