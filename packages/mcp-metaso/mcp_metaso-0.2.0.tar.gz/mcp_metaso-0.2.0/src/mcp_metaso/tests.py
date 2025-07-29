"""MCP Metaso测试模块

提供单元测试和集成测试功能，验证各个组件的正确性。
"""
import asyncio
import os
import sys
from typing import Dict, Any

from .config import Config
from .server import create_server
from .utils import (
    validate_url,
    validate_scope,
    validate_size,
    sanitize_query,
    format_duration,
    truncate_text,
    extract_domain,
    format_authors,
    parse_search_params,
)
from .formatters import SCOPE_RESULT_MAPPING, SCOPE_CN_MAPPING


def test_config() -> bool:
    """测试配置模块
    
    Returns:
        bool: 测试是否通过
    """
    print("测试配置模块...")
    
    try:
        # 测试配置创建
        config = Config()
        assert hasattr(config, 'api_key')
        assert hasattr(config, 'base_url')
        assert hasattr(config, 'timeout')
        
        # 测试配置验证
        assert isinstance(config.validate(), bool)
        
        # 测试字符串表示
        repr_str = repr(config)
        assert "Config" in repr_str
        
        print("✅ 配置模块测试通过")
        return True
    except Exception as e:
        print(f"❌ 配置模块测试失败: {e}")
        return False


def test_utils() -> bool:
    """测试工具函数
    
    Returns:
        bool: 测试是否通过
    """
    print("测试工具函数...")
    
    try:
        # 测试URL验证
        assert validate_url("https://example.com") == True
        assert validate_url("invalid-url") == False
        
        # 测试搜索范围验证
        assert validate_scope("webpage") == True
        assert validate_scope("invalid") == False
        
        # 测试结果数量验证
        assert validate_size(10) == True
        assert validate_size(0) == False
        assert validate_size(25) == False
        
        # 测试查询词清理
        assert sanitize_query("  test query  ") == "test query"
        assert sanitize_query("test<script>") == "testscript"
        
        # 测试时长格式化
        assert format_duration(30) == "30秒"
        assert format_duration(90) == "1分30秒"
        assert format_duration(3661) == "1小时1分1秒"
        
        # 测试文本截断
        assert truncate_text("short", 10) == "short"
        assert truncate_text("very long text", 8) == "very ..."
        
        # 测试域名提取
        assert extract_domain("https://example.com/path") == "example.com"
        assert extract_domain("invalid-url") is None
        
        # 测试作者格式化
        assert format_authors(["作者1", "作者2"]) == "作者1, 作者2"
        assert format_authors("单个作者") == "单个作者"
        assert format_authors(None) == "N/A"
        
        # 测试搜索参数解析
        params = {
            "query": "  test  ",
            "scope": "webpage",
            "size": "5",
            "include_summary": "true"
        }
        parsed = parse_search_params(params)
        assert parsed["query"] == "test"
        assert parsed["scope"] == "webpage"
        assert parsed["size"] == 5
        assert parsed["include_summary"] == True
        
        print("✅ 工具函数测试通过")
        return True
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False


def test_formatters() -> bool:
    """测试格式化器
    
    Returns:
        bool: 测试是否通过
    """
    print("测试格式化器...")
    
    try:
        # 测试映射常量
        assert "webpage" in SCOPE_RESULT_MAPPING
        assert "webpage" in SCOPE_CN_MAPPING
        assert len(SCOPE_RESULT_MAPPING) == len(SCOPE_CN_MAPPING)
        
        # 测试所有支持的搜索类型
        expected_scopes = {"webpage", "document", "scholar", "image", "video", "podcast"}
        assert set(SCOPE_RESULT_MAPPING.keys()) == expected_scopes
        assert set(SCOPE_CN_MAPPING.keys()) == expected_scopes
        
        print("✅ 格式化器测试通过")
        return True
    except Exception as e:
        print(f"❌ 格式化器测试失败: {e}")
        return False


def test_server_creation() -> bool:
    """测试服务器创建
    
    Returns:
        bool: 测试是否通过
    """
    print("测试服务器创建...")
    
    try:
        # 创建服务器实例
        server = create_server()
        assert server is not None
        
        # 检查工具是否正确注册
        tools = server.list_tools()
        tool_names = [tool.name for tool in tools]
        
        assert "metaso_search" in tool_names
        assert "metaso_reader" in tool_names
        
        print("✅ 服务器创建测试通过")
        return True
    except Exception as e:
        print(f"❌ 服务器创建测试失败: {e}")
        return False


async def test_search_tool() -> bool:
    """测试搜索工具（需要API密钥）
    
    Returns:
        bool: 测试是否通过
    """
    print("测试搜索工具...")
    
    # 检查是否有API密钥
    if not os.getenv("METASO_API_KEY"):
        print("⚠️  跳过搜索工具测试（未设置API密钥）")
        return True
    
    try:
        server = create_server()
        tools = server.list_tools()
        
        # 找到搜索工具
        search_tool = None
        for tool in tools:
            if tool.name == "metaso_search":
                search_tool = tool
                break
        
        assert search_tool is not None
        
        # 测试搜索功能
        result = await search_tool.call({
            "query": "测试查询",
            "scope": "webpage",
            "include_summary": False,
            "size": 3
        })
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        print("✅ 搜索工具测试通过")
        return True
    except Exception as e:
        print(f"❌ 搜索工具测试失败: {e}")
        return False


async def test_reader_tool() -> bool:
    """测试网页解析工具（需要API密钥）
    
    Returns:
        bool: 测试是否通过
    """
    print("测试网页解析工具...")
    
    # 检查是否有API密钥
    if not os.getenv("METASO_API_KEY"):
        print("⚠️  跳过网页解析工具测试（未设置API密钥）")
        return True
    
    try:
        server = create_server()
        tools = server.list_tools()
        
        # 找到解析工具
        reader_tool = None
        for tool in tools:
            if tool.name == "metaso_reader":
                reader_tool = tool
                break
        
        assert reader_tool is not None
        
        # 测试网页解析功能
        result = await reader_tool.call({
            "url": "https://example.com",
            "output_format": "markdown"
        })
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        print("✅ 网页解析工具测试通过")
        return True
    except Exception as e:
        print(f"❌ 网页解析工具测试失败: {e}")
        return False


def run_all_tests() -> bool:
    """运行所有测试
    
    Returns:
        bool: 所有测试是否通过
    """
    print("🧪 开始运行MCP Metaso测试套件")
    print("=" * 50)
    
    test_results = []
    
    # 运行同步测试
    test_results.append(test_config())
    test_results.append(test_utils())
    test_results.append(test_formatters())
    test_results.append(test_server_creation())
    
    # 运行异步测试
    async def run_async_tests():
        async_results = []
        async_results.append(await test_search_tool())
        async_results.append(await test_reader_tool())
        return async_results
    
    async_results = asyncio.run(run_async_tests())
    test_results.extend(async_results)
    
    # 统计结果
    passed = sum(test_results)
    total = len(test_results)
    
    print("=" * 50)
    print(f"测试完成: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print(f"❌ {total - passed} 个测试失败")
        return False


def main() -> None:
    """测试主函数"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"测试运行出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()