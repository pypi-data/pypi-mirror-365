"""MCP Metaso实用工具模块

提供各种实用工具函数，包括验证、格式化、错误处理等功能。
"""
import re
import urllib.parse
from typing import Dict, Any, Optional, List


def validate_url(url: str) -> bool:
    """验证URL格式是否正确
    
    Args:
        url: 要验证的URL字符串
        
    Returns:
        bool: URL是否有效
    """
    try:
        result = urllib.parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_scope(scope: str) -> bool:
    """验证搜索范围是否有效
    
    Args:
        scope: 搜索范围
        
    Returns:
        bool: 搜索范围是否有效
    """
    valid_scopes = {"webpage", "document", "scholar", "image", "video", "podcast"}
    return scope in valid_scopes


def validate_size(size: int) -> bool:
    """验证结果数量是否在有效范围内
    
    Args:
        size: 结果数量
        
    Returns:
        bool: 结果数量是否有效
    """
    return 1 <= size <= 20


def sanitize_query(query: str) -> str:
    """清理搜索查询词
    
    Args:
        query: 原始查询词
        
    Returns:
        str: 清理后的查询词
    """
    # 移除多余的空白字符
    query = re.sub(r'\s+', ' ', query.strip())
    
    # 移除潜在的危险字符
    query = re.sub(r'[<>"\']', '', query)
    
    return query


def format_duration(seconds: int) -> str:
    """格式化时长显示
    
    Args:
        seconds: 秒数
        
    Returns:
        str: 格式化的时长字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}分{remaining_seconds}秒"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        remaining_seconds = seconds % 60
        return f"{hours}小时{remaining_minutes}分{remaining_seconds}秒"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """截断文本到指定长度
    
    Args:
        text: 要截断的文本
        max_length: 最大长度
        suffix: 截断后的后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_domain(url: str) -> Optional[str]:
    """从URL中提取域名
    
    Args:
        url: URL字符串
        
    Returns:
        Optional[str]: 域名，如果提取失败则返回None
    """
    try:
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def safe_get(data: Dict[str, Any], key: str, default: Any = "N/A") -> Any:
    """安全地从字典中获取值
    
    Args:
        data: 数据字典
        key: 键名
        default: 默认值
        
    Returns:
        Any: 键对应的值或默认值
    """
    return data.get(key, default)


def format_authors(authors: Any) -> str:
    """格式化作者信息
    
    Args:
        authors: 作者信息，可能是字符串、列表或其他类型
        
    Returns:
        str: 格式化后的作者字符串
    """
    if isinstance(authors, list):
        return ', '.join(str(author) for author in authors if author)
    elif isinstance(authors, str):
        return authors
    elif authors is None:
        return "N/A"
    else:
        return str(authors)


def create_error_response(error_type: str, message: str, details: Optional[str] = None) -> str:
    """创建标准化的错误响应
    
    Args:
        error_type: 错误类型
        message: 错误消息
        details: 详细信息（可选）
        
    Returns:
        str: 格式化的错误响应
    """
    response = f"❌ {error_type}: {message}"
    if details:
        response += f"\n\n详细信息: {details}"
    return response


def create_success_response(title: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
    """创建标准化的成功响应
    
    Args:
        title: 响应标题
        content: 响应内容
        metadata: 元数据（可选）
        
    Returns:
        str: 格式化的成功响应
    """
    response = f"# {title}\n\n{content}"
    
    if metadata:
        response += "\n\n## 元数据\n"
        for key, value in metadata.items():
            response += f"- **{key}**: {value}\n"
    
    return response


def validate_api_response(response_data: Dict[str, Any], required_fields: List[str]) -> bool:
    """验证API响应数据的完整性
    
    Args:
        response_data: API响应数据
        required_fields: 必需的字段列表
        
    Returns:
        bool: 响应数据是否有效
    """
    if not isinstance(response_data, dict):
        return False
    
    for field in required_fields:
        if field not in response_data:
            return False
    
    return True


def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """遮蔽敏感数据
    
    Args:
        data: 敏感数据字符串
        mask_char: 遮蔽字符
        visible_chars: 可见字符数量
        
    Returns:
        str: 遮蔽后的字符串
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    visible_part = data[:visible_chars]
    masked_part = mask_char * (len(data) - visible_chars)
    return visible_part + masked_part


def parse_search_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """解析和验证搜索参数
    
    Args:
        params: 原始搜索参数
        
    Returns:
        Dict[str, Any]: 验证后的搜索参数
        
    Raises:
        ValueError: 当参数无效时抛出异常
    """
    validated_params = {}
    
    # 验证查询词
    query = params.get("query", "").strip()
    if not query:
        raise ValueError("查询词不能为空")
    validated_params["query"] = sanitize_query(query)
    
    # 验证搜索范围
    scope = params.get("scope", "webpage")
    if not validate_scope(scope):
        raise ValueError(f"无效的搜索范围: {scope}")
    validated_params["scope"] = scope
    
    # 验证结果数量
    size = params.get("size", 10)
    try:
        size = int(size)
    except (ValueError, TypeError):
        raise ValueError("结果数量必须是整数")
    
    if not validate_size(size):
        raise ValueError("结果数量必须在1-20之间")
    validated_params["size"] = size
    
    # 验证摘要选项
    include_summary = params.get("include_summary", False)
    if isinstance(include_summary, str):
        include_summary = include_summary.lower() in ("true", "1", "yes")
    validated_params["include_summary"] = bool(include_summary)
    
    return validated_params