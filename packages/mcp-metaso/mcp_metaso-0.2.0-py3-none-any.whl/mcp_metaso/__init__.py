"""MCP Metaso - 基于MCP协议的Metaso AI搜索引擎服务器

这是一个基于Model Context Protocol (MCP)的Metaso AI搜索引擎服务器实现，
提供多维搜索和网页解析功能。
"""

__version__ = "0.2.0"
__author__ = "MCP Metaso Team"
__email__ = "support@example.com"
__description__ = "基于MCP协议的Metaso AI搜索引擎服务器"

# 导出主要组件
from .config import Config, config
from .server import create_server, main as server_main
from .cli import main as cli_main
from .utils import (
    validate_url,
    validate_scope,
    validate_size,
    sanitize_query,
    format_duration,
    truncate_text,
    extract_domain,
    safe_get,
    format_authors,
    create_error_response,
    create_success_response,
    validate_api_response,
    mask_sensitive_data,
    parse_search_params,
)
from .formatters import (
    RESULT_FORMATTERS,
    SCOPE_RESULT_MAPPING,
    SCOPE_CN_MAPPING,
)

__all__ = [
    # 核心组件
    "Config",
    "config", 
    "create_server",
    "server_main",
    "cli_main",
    
    # 工具函数
    "validate_url",
    "validate_scope",
    "validate_size",
    "sanitize_query",
    "format_duration",
    "truncate_text",
    "extract_domain",
    "safe_get",
    "format_authors",
    "create_error_response",
    "create_success_response",
    "validate_api_response",
    "mask_sensitive_data",
    "parse_search_params",
    
    # 格式化器
    "RESULT_FORMATTERS",
    "SCOPE_RESULT_MAPPING",
    "SCOPE_CN_MAPPING",
    
    # 元数据
    "__version__",
    "__author__",
    "__email__",
    "__description__",
]