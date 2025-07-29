# MCP Metaso

> 一个基于 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 的 Metaso AI 搜索引擎服务器，使用官方 FastMCP SDK 构建。现已支持 uvx 包管理！

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-1.12.2+-green.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PyPI](https://img.shields.io/badge/PyPI-0.2.0-orange.svg)](https://pypi.org/project/mcp-metaso/)

## ✨ 功能特性

- 🔍 **多维搜索**：支持网页、文库、学术、图片、视频、播客六种搜索类型
- 📄 **网页解析**：提取网页内容并转换为 Markdown 或 JSON 格式
- ⚡ **高性能**：基于 FastMCP SDK，异步处理，类型安全
- 🔌 **标准兼容**：完全符合 MCP 协议规范，可与 Claude Desktop 等客户端集成
- 📦 **uvx 支持**：可通过 uvx 直接运行，无需本地安装
- 🛠️ **模块化设计**：清晰的包结构，易于扩展和维护

## 🚀 快速开始

### 方式一：使用 uvx（推荐）

```bash
# 直接运行服务器
uvx mcp-metaso server

# 测试搜索功能
uvx mcp-metaso test-search "人工智能发展趋势"

# 测试网页解析
uvx mcp-metaso test-reader "https://example.com"

# 查看配置信息
uvx mcp-metaso config
```

### 方式二：传统安装

```bash
# 安装包
pip install mcp-metaso

# 配置 API 密钥
export METASO_API_KEY="your-api-key-here"

# 启动服务器
mcp-metaso server

# 或者使用 Python 模块
python -m mcp_metaso.server
```

### 方式三：开发模式

```bash
# 克隆项目
git clone <repository-url>
cd mcp-metaso

# 安装开发依赖
pip install -e .[dev]

# 运行测试
python -m mcp_metaso.tests

# 启动服务器
python -m mcp_metaso.cli server
```

## 🔧 Claude Desktop 集成

### 使用 uvx（推荐方式）

使用 uvx 可以让 Claude Desktop 集成变得更加简单和可靠：

```json
{
  "mcpServers": {
    "mcp-metaso": {
      "command": "uvx",
      "args": ["mcp-metaso", "server"],
      "env": {
        "METASO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 传统安装方式

如果您已经安装了包，可以使用以下配置：

```json
{
  "mcpServers": {
    "mcp-metaso": {
      "command": "mcp-metaso-server",
      "env": {
        "METASO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### 开发模式配置

对于开发环境，可以使用项目提供的启动脚本：

```json
{
  "mcpServers": {
    "mcp-metaso": {
      "command": "python",
      "args": ["/path/to/mcp-metaso/run.py", "server"],
      "env": {
        "METASO_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

或者使用 PYTHONPATH 方式：

```json
{
  "mcpServers": {
    "mcp-metaso": {
      "command": "python",
      "args": ["-m", "mcp_metaso.server"],
      "env": {
        "METASO_API_KEY": "your-api-key-here",
        "PYTHONPATH": "/path/to/mcp-metaso/src"
      }
    }
  }
}
```

**配置文件位置：**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 验证配置

安装完成后，验证配置是否正确：

```bash
# 使用 uvx 验证
uvx mcp-metaso config

# 测试搜索功能
uvx mcp-metaso test-search "测试查询"

# 运行完整测试套件
uvx mcp-metaso --help
```

### 故障排除

如果Claude Desktop没有显示🔨图标：

1. **重启Claude Desktop** - 配置更改需要重启应用
2. **检查命令** - 确保 `uvx` 或 `mcp-metaso-server` 命令可用
3. **验证API密钥** - 确保METASO_API_KEY已正确设置
4. **查看日志** - 检查Claude Desktop日志文件夹中的错误信息
5. **测试命令** - 在终端中手动运行配置的命令确保其工作正常

## 📖 可用工具

### metaso_search

多维搜索工具，支持六种搜索类型：

```python
metaso_search(
    query="人工智能发展趋势",  # 搜索查询词
    scope="webpage",           # 搜索类型：webpage/document/scholar/image/video/podcast
    include_summary=False,     # 是否包含 AI 摘要
    size=10                   # 结果数量 (1-20)
)
```

**搜索类型说明：**
- `webpage` - 网页搜索：新闻、博客、资讯
- `document` - 文库搜索：PDF 文档、技术文档
- `scholar` - 学术搜索：论文、研究文献
- `image` - 图片搜索：图片、图表、插图
- `video` - 视频搜索：教程、演讲、娱乐内容
- `podcast` - 播客搜索：音频节目、访谈

### metaso_reader

网页内容解析工具：

```python
metaso_reader(
    url="https://example.com",  # 网页 URL
    output_format="markdown"    # 输出格式：markdown/json
)
```

## 📁 项目结构

```
mcp-metaso/
├── src/
│   └── mcp_metaso/               # 主包目录
│       ├── __init__.py           # 包初始化和导出
│       ├── __main__.py           # 模块主入口点
│       ├── config.py             # 配置管理模块
│       ├── server.py             # MCP服务器实现
│       ├── cli.py                # 命令行接口
│       ├── formatters.py         # 搜索结果格式化器
│       ├── utils.py              # 实用工具函数
│       └── tests.py              # 测试模块
├── run.py                        # 开发启动脚本（无需安装）
├── pyproject.toml                # 项目配置和依赖
├── requirements.txt              # 兼容性依赖文件
├── test_all_scopes.py            # 兼容性测试脚本
├── LICENSE                       # 开源许可证
└── README.md                     # 项目说明文档
```

### 模块说明

- **`__init__.py`**: 包初始化文件，定义包的公共接口和版本信息
- **`__main__.py`**: 模块主入口点，支持 `python -m mcp_metaso` 运行方式
- **`config.py`**: 配置管理模块，支持环境变量配置和验证
- **`server.py`**: FastMCP服务器实现，提供搜索和解析工具
- **`cli.py`**: 命令行接口，支持服务器启动、测试等功能
- **`formatters.py`**: 搜索结果格式化器，支持多种搜索类型
- **`utils.py`**: 实用工具函数，包括验证、格式化、错误处理等
- **`tests.py`**: 完整的测试套件，支持单元测试和集成测试
- **`run.py`**: 开发启动脚本，无需安装包即可运行，方便开发和调试

## 🔨 开发

### 环境要求

- Python 3.11+
- Metaso API Key
- uvx (推荐) 或 pip

### 本地开发设置

```bash
# 克隆仓库
git clone https://github.com/HundunOnline/mcp-metaso.git
cd mcp-metaso

# 方式1: 使用 uvx 进行开发（推荐）
uvx --from . mcp-metaso --help

# 方式2: 传统方式安装开发依赖
pip install -e ".[dev]"

# 方式3: 使用启动脚本（无需安装）
python run.py --help

# 设置环境变量
export METASO_API_KEY="your-api-key-here"

# 运行测试（根据安装方式选择）
python run.py config                    # 使用启动脚本
# 或
python -m mcp_metaso.tests             # 需要设置PYTHONPATH

# 启动开发服务器
python run.py server                    # 使用启动脚本
# 或
PYTHONPATH=src python -m mcp_metaso.server  # 使用模块方式
```

### 测试功能

```bash
# 使用 uvx 测试
uvx --from . mcp-metaso test-search "测试查询"
uvx --from . mcp-metaso test-reader "https://example.com"
uvx --from . mcp-metaso config

# 使用启动脚本（推荐开发时使用）
python run.py test-search "测试查询"
python run.py test-reader "https://example.com"
python run.py config

# 或者使用 Python 模块（需要设置PYTHONPATH）
PYTHONPATH=src python -m mcp_metaso test-search "测试查询"
PYTHONPATH=src python -m mcp_metaso test-reader "https://example.com"
PYTHONPATH=src python -m mcp_metaso config

# 运行完整测试套件
python run.py --help  # 查看所有可用命令
```

### 代码质量

```bash
# 格式化代码
black src/

# 排序导入
isort src/

# 类型检查
mypy src/

# 运行所有质量检查
python -c "import subprocess; subprocess.run(['black', 'src/']); subprocess.run(['isort', 'src/']); subprocess.run(['mypy', 'src/'])"
```

### 构建和发布

```bash
# 构建包
python -m build

# 检查包
twine check dist/*

# 发布到PyPI
twine upload dist/*

# 使用 uvx 测试已发布的包
uvx mcp-metaso --help
```



### 添加新功能

使用 FastMCP 装饰器可以轻松添加新工具：

```python
@mcp.tool()
async def new_tool(param: str) -> str:
    """新工具描述
    
    Args:
        param: 参数描述
    """
    # 实现逻辑
    return result
```

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 🔗 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Metaso AI](https://metaso.cn/)