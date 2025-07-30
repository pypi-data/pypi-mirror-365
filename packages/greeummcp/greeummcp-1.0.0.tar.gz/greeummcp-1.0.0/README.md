# GreeumMCP

GreeumMCP is a Model Context Protocol (MCP) server implementation for the Greeum Memory Engine. It enables seamless integration of Greeum's powerful memory capabilities with Large Language Models (LLMs) that support the MCP standard, such as Claude.

## Features

- **Memory Management**: Store, retrieve, and search through long-term and short-term memories
- **Time-based Recall**: Search memories based on temporal references like "yesterday" or "two weeks ago"
- **Semantic Search**: Find memories based on semantic similarity
- **Memory Enrichment**: Automatically extract keywords, tags, and compute importance scores
- **Multiple Transport Options**: Supports stdio, HTTP, and WebSocket transports
- **Claude Desktop Integration**: Ready to use with Claude Desktop

## Installation

### 🚀 빠른 설치 (UV 사용 - 권장)

<details open>
<summary>설치 없이 바로 실행 (uvx)</summary>

```bash
# UV 설치 (처음 한 번만)
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# GreeumMCP 실행 (설치 없이)
uvx greeummcp
```

</details>

### 📦 일반 설치 (pip)

<details>
<summary>Linux / macOS (bash / zsh)</summary>

```bash
# 1) 가상 환경(권장)
python3 -m venv venv && source venv/bin/activate

# 2) 최신 안정판 설치
pip install greeummcp

# 3) 개발 도구까지 설치하려면
pip install "greeummcp[dev]"
```

</details>

<details>
<summary>Windows (PowerShell)</summary>

```powershell
# 1) 가상 환경(권장)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2) 패키지 설치
pip install greeummcp
```

</details>

### 📋 필수 조건
- Python 3.10 이상
- `greeum` v0.6.1 이상은 greeummcp가 자동으로 의존성으로 설치합니다.
- (선택) C/C++ Build Tools – 일부 확장 기능에서 필요할 수 있습니다.

### ✅ 설치 확인

```bash
# pip 설치 시
greeummcp version

# uvx 사용 시
uvx greeummcp version
```

위 명령이 버전 문자열(예: `0.2.4`)을 출력하면 설치가 완료된 것입니다.

---
### 빠른 시작

```bash
# 기본 실행 (data 디렉토리는 ./data 사용)
greeummcp

# 커스텀 데이터 디렉토리 지정
greeummcp /path/to/data

# HTTP transport 사용
greeummcp --transport http --port 8000
```

---
### Claude Desktop 연동

#### 🌟 방법 1: UV 사용 (가장 간단)

<details open>
<summary>모든 OS 공통</summary>

```json
{
  "mcpServers": {
    "greeum_mcp": {
      "command": "uvx",
      "args": ["greeummcp"]
    }
  }
}
```

커스텀 데이터 디렉토리 지정:
```json
{
  "mcpServers": {
    "greeum_mcp": {
      "command": "uvx",
      "args": ["greeummcp", "/path/to/data"]
    }
  }
}
```

</details>

#### 📦 방법 2: pip 설치 후 사용

<details>
<summary>Windows</summary>

```json
{
  "mcpServers": {
    "greeum_mcp": {
      "command": "greeummcp.exe",
      "args": ["C:\\Users\\USERNAME\\greeum-data"]
    }
  }
}
```

기본 설정 (./data 사용):
```json
{
  "mcpServers": {
    "greeum_mcp": {
      "command": "greeummcp.exe"
    }
  }
}
```
</details>

<details>
<summary>macOS / Linux</summary>

```json
{
  "mcpServers": {
    "greeum_mcp": {
      "command": "greeummcp",
      "args": ["/home/username/greeum-data"]
    }
  }
}
```

기본 설정 (./data 사용):
```json
{
  "mcpServers": {
    "greeum_mcp": {
      "command": "greeummcp"
    }
  }
}
```
</details>

1. 위 설정을 `claude_desktop_config.json`에 추가합니다.
2. Claude Desktop 재시작 → 🔨 아이콘 클릭해 Tool 목록에 **greeum_mcp** 가 나타나는지 확인.

---
### Cursor IDE 연동
프로젝트 루트에 `.cursor/mcp.json` 파일을 생성:

```json
{
  "greeum_mcp": {
    "command": "greeummcp",
    "args": ["${workspaceFolder}/data"]
  }
}
```

저장 후 Cursor를 재시작하면 MCP 툴이 자동으로 로드됩니다.

---

## Quick Start

### Running as a Command-Line Tool

GreeumMCP can be run directly from the command line:

```bash
# Run with default settings (stdio transport, ./data directory)
greeummcp

# Specify custom data directory
greeummcp /path/to/data

# Using HTTP transport
greeummcp --transport http --port 8000

# Legacy command (still supported)
greeum_mcp --data-dir ./data --transport stdio
```

### Using as a Python Library

```python
from greeummcp import run_server

# Run with default settings
run_server()

# Run with custom settings
run_server(
    data_dir="./data",
    server_name="greeum_mcp",
    port=8000,
    transport="http",
    greeum_config={
        "ttl_short": 3600,  # 1 hour
        "ttl_medium": 86400,  # 1 day
        "ttl_long": 604800,  # 1 week
        "default_language": "auto"
    }
)
```

## Claude Desktop Integration

GreeumMCP can be used with Claude Desktop to provide memory capabilities to Claude. The package includes a helper script to set up the integration:

```bash
# Run the Claude Desktop integration helper
python examples/claude_desktop.py

# Create the Claude Desktop configuration file
python examples/claude_desktop.py --create --data-dir ./data
```

After setting up, restart Claude Desktop, and you should see the GreeumMCP tools available in the tools panel (hammer icon).

### Manual Configuration for Claude Desktop

You can also manually configure Claude Desktop to use GreeumMCP by creating a JSON configuration file:

1. Locate or create the Claude Desktop configuration file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Add the GreeumMCP server configuration to this file:

#### Windows Example:
```json
{
    "mcpServers": {
        "greeum_mcp": {
            "command": "python",
            "args": [
                "-m", "greeummcp.server",
                "--data-dir", "C:\\Users\\USERNAME\\Documents\\greeum-data",
                "--transport", "stdio"
            ]
        }
    }
}
```

#### macOS/Linux Example:
```json
{
    "mcpServers": {
        "greeum_mcp": {
            "command": "python3",
            "args": [
                "-m", "greeummcp.server",
                "--data-dir", "/Users/USERNAME/Documents/greeum-data",
                "--transport", "stdio"
            ]
        }
    }
}
```

3. Make sure to replace `USERNAME` and adjust paths according to your system.
4. Restart Claude Desktop to apply the changes.
5. Verify that the tools are available by looking for the hammer icon in the Claude Desktop interface.

### Cursor Integration

To use GreeumMCP with Cursor, create a `.cursor/mcp.json` file in your project root:

```json
{
  "greeum_mcp": {
    "command": "python",
    "args": ["-m", "greeummcp.server", "--data-dir", "YOUR_DATA_DIR", "--transport", "stdio", "--server-name", "greeum_mcp"]
  }
}
```

#### Important Notes

- **Server naming**: Always use underscores (`_`) instead of hyphens (`-`) in server names to avoid MCP compatibility issues.
- **Data directory**: Use an absolute path for the data directory to ensure reliability.

### Verifying the Integration

To verify that GreeumMCP is working properly with Claude Desktop:

1. Click the hammer icon in Claude Desktop.
2. You should see GreeumMCP tools listed (like add_memory, query_memory, etc.).
3. Try adding a memory with a query like "Save this information: Claude was developed by Anthropic."
4. Then try retrieving it with "What information do you have about Claude?"

If you encounter issues:
- Check Claude Desktop logs in `~/Library/Logs/Claude/` (macOS) or `%APPDATA%\Claude\Logs` (Windows)
- Ensure the GreeumMCP server is properly installed and paths are correct
- Verify your configuration file has the correct syntax

## Memory Tools

GreeumMCP provides the following memory-related tools:

- **add_memory**: Add a new memory to long-term storage
- **query_memory**: Search memories by query text
- **retrieve_memory**: Retrieve a specific memory by ID
- **update_memory**: Update an existing memory
- **delete_memory**: Delete a memory by ID
- **search_time**: Search memories based on time references
- **generate_prompt**: Generate a prompt that includes relevant memories
- **extract_keywords**: Extract keywords from text
- **verify_chain**: Verify the integrity of the memory blockchain
- **server_status**: Get server status information

## Example Usage

### Interactive CLI

GreeumMCP includes an interactive CLI example for trying out the memory capabilities:

```bash
python examples/cli_example.py --data-dir ./data
```

This opens an interactive shell where you can:

```
greeum> add This is my first memory
Memory added with ID: 1

greeum> add This is my second memory about Python
Memory added with ID: 2

greeum> search Python
Found 1 results:

--- Result 1 ---
ID: 2
Content: This is my second memory about Python
Timestamp: 2023-07-01T12:34:56
Keywords: memory, Python, second
Importance: 0.65
```

## Development

### Project Structure

```
GreeumMCP/
├── greeummcp/                   # Main package
│   ├── __init__.py              # Package initialization
│   ├── server.py                # MCP server implementation
│   ├── tools/                   # MCP tools implementation
│   ├── resources/               # MCP resources implementation
│   ├── prompts/                 # MCP prompts implementation
│   └── adapters/                # Greeum integration adapters
├── examples/                    # Usage examples
├── tests/                       # Tests
├── README.md                    # Project documentation
├── setup.py                     # Package setup
└── requirements.txt             # Dependencies
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## License

GreeumMCP is licensed under the MIT License.

## Acknowledgments

- GreeumMCP is built on the [Model Context Protocol](https://modelcontextprotocol.io) standard
- GreeumMCP uses the [Greeum Memory Engine](https://github.com/GreeumAI/Greeum) as its core component
