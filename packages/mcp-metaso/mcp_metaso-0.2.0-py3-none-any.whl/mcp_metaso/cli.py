"""MCP Metaso命令行接口

提供命令行工具，支持直接运行服务器、测试功能等操作。
"""
import argparse
import asyncio
import sys
from typing import Optional

from .config import config
from .server import main as server_main, create_server
from . import __version__


def test_search(query: str, scope: str = "webpage") -> None:
    """测试搜索功能
    
    Args:
        query: 搜索查询词
        scope: 搜索范围
    """
    async def _test_search():
        """异步测试搜索功能"""
        if not config.api_key:
            print("错误: 未设置METASO_API_KEY环境变量")
            print("请设置API密钥后重试: export METASO_API_KEY='your_key_here'")
            return
        
        server = create_server()
        # 获取搜索工具
        tools = server.list_tools()
        search_tool = None
        for tool in tools:
            if tool.name == "metaso_search":
                search_tool = tool
                break
        
        if not search_tool:
            print("错误: 未找到搜索工具")
            return
        
        print(f"正在搜索: {query} (范围: {scope})")
        print("-" * 50)
        
        try:
            # 调用搜索工具
            result = await search_tool.call({
                "query": query,
                "scope": scope,
                "include_summary": False,
                "size": 5
            })
            print(result)
        except Exception as e:
            print(f"搜索失败: {e}")
    
    asyncio.run(_test_search())


def test_reader(url: str, output_format: str = "markdown") -> None:
    """测试网页解析功能
    
    Args:
        url: 要解析的网页URL
        output_format: 输出格式
    """
    async def _test_reader():
        """异步测试网页解析功能"""
        if not config.api_key:
            print("错误: 未设置METASO_API_KEY环境变量")
            print("请设置API密钥后重试: export METASO_API_KEY='your_key_here'")
            return
        
        server = create_server()
        # 获取解析工具
        tools = server.list_tools()
        reader_tool = None
        for tool in tools:
            if tool.name == "metaso_reader":
                reader_tool = tool
                break
        
        if not reader_tool:
            print("错误: 未找到网页解析工具")
            return
        
        print(f"正在解析网页: {url}")
        print("-" * 50)
        
        try:
            # 调用解析工具
            result = await reader_tool.call({
                "url": url,
                "output_format": output_format
            })
            print(result)
        except Exception as e:
            print(f"网页解析失败: {e}")
    
    asyncio.run(_test_reader())


def show_config() -> None:
    """显示当前配置信息"""
    print("MCP Metaso 配置信息:")
    print("-" * 30)
    print(f"版本: {__version__}")
    print(f"API密钥: {'已设置' if config.api_key else '未设置'}")
    print(f"基础URL: {config.base_url}")
    print(f"超时时间: {config.timeout}秒")
    print(f"配置有效: {'是' if config.validate() else '否'}")
    
    if not config.api_key:
        print("\n⚠️  警告: 未设置API密钥，搜索功能不可用")
        print("请设置环境变量: export METASO_API_KEY='your_key_here'")


def main() -> None:
    """主命令行入口点
    
    解析命令行参数并执行相应的操作。
    """
    parser = argparse.ArgumentParser(
        description="MCP Metaso - 基于MCP协议的Metaso AI搜索引擎服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s server                    # 启动MCP服务器
  %(prog)s test-search "人工智能"      # 测试搜索功能
  %(prog)s test-reader "https://example.com"  # 测试网页解析
  %(prog)s config                    # 显示配置信息
  %(prog)s --version                 # 显示版本信息
"""
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"mcp-metaso {__version__}"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="可用命令",
        metavar="COMMAND"
    )
    
    # 服务器命令
    server_parser = subparsers.add_parser(
        "server",
        help="启动MCP服务器"
    )
    
    # 测试搜索命令
    test_search_parser = subparsers.add_parser(
        "test-search",
        help="测试搜索功能"
    )
    test_search_parser.add_argument(
        "query",
        help="搜索查询词"
    )
    test_search_parser.add_argument(
        "--scope",
        choices=["webpage", "document", "scholar", "image", "video", "podcast"],
        default="webpage",
        help="搜索范围 (默认: webpage)"
    )
    
    # 测试网页解析命令
    test_reader_parser = subparsers.add_parser(
        "test-reader",
        help="测试网页解析功能"
    )
    test_reader_parser.add_argument(
        "url",
        help="要解析的网页URL"
    )
    test_reader_parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式 (默认: markdown)"
    )
    
    # 配置信息命令
    config_parser = subparsers.add_parser(
        "config",
        help="显示配置信息"
    )
    
    args = parser.parse_args()
    
    # 如果没有提供命令，默认启动服务器
    if not args.command:
        print("未指定命令，启动MCP服务器...")
        print("使用 --help 查看所有可用命令")
        print()
        server_main()
        return
    
    # 执行相应的命令
    try:
        if args.command == "server":
            server_main()
        elif args.command == "test-search":
            test_search(args.query, args.scope)
        elif args.command == "test-reader":
            test_reader(args.url, args.format)
        elif args.command == "config":
            show_config()
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()