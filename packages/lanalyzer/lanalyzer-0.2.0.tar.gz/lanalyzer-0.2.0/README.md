![Lanalyzer](https://raw.githubusercontent.com/bayuncao/lanalyzer/0fe337cfa47121d987b692d621090ca678431c93/image/banner.png)

# Lanalyzer

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![uv](https://img.shields.io/badge/uv-0.1.18+-purple.svg)](https://github.com/astral-sh/uv)
[![PyPI version](https://img.shields.io/pypi/v/lanalyzer.svg?logo=pypi&label=pypi&color=blue)](https://pypi.org/project/lanalyzer/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/bayuncao/lanalyzer/ci.yml?branch=main&style=flat-square)](https://github.com/bayuncao/lanalyzer/actions)
[![Code Coverage](https://img.shields.io/codecov/c/github/bayuncao/lanalyzer.svg?style=flat-square)](https://codecov.io/gh/bayuncao/lanalyzer)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](CONTRIBUTING.md)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

Lanalyzer is an advanced Python static taint analysis tool designed to detect potential security vulnerabilities in Python projects. It identifies data flows from untrusted sources (Sources) to sensitive operations (Sinks) and provides detailed insights into potential risks.

## 📖 Table of Contents

- [Lanalyzer](#lanalyzer)
  - [📖 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🚀 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
      - [Option 1: Install from PyPI (Recommended)](#option-1-install-from-pypi-recommended)
      - [Option 2: Install from Source](#option-2-install-from-source)
  - [💻 Usage](#-usage)
    - [Basic Analysis](#basic-analysis)
    - [Command-Line Options](#command-line-options)
    - [Example](#example)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [📞 Contact](#-contact)
    - [Contact](#contact)
  - [🧩 Model Context Protocol (MCP) Support](#-model-context-protocol-mcp-support)
    - [Installing MCP Dependencies](#installing-mcp-dependencies)
    - [Starting the MCP Server](#starting-the-mcp-server)
    - [MCP Server Features](#mcp-server-features)
    - [Integration with AI Tools](#integration-with-ai-tools)
    - [Using in Cursor](#using-in-cursor)
    - [MCP Command-Line Options](#mcp-command-line-options)
    - [Advanced MCP Usage](#advanced-mcp-usage)
      - [Custom Configurations](#custom-configurations)
      - [Batch File Analysis](#batch-file-analysis)
  - [📊 Analysis Results Format](#-analysis-results-format)

## ✨ Features

- **Taint Analysis**: Tracks data flows from sources to sinks.
- **Customizable Rules**: Define your own sources, sinks, sanitizers, and taint propagation paths.
- **Static Analysis**: No need to execute the code.
- **Extensibility**: Easily add new rules for detecting vulnerabilities like SQL Injection, XSS, and more.
- **Detailed Reports**: Generate comprehensive analysis reports with vulnerability details and mitigation suggestions.
- **Command-Line Interface**: Run analyses directly from the terminal.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended for dependency management)

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
# Using pip
pip install lanalyzer

# Install as a tool (recommended)
uv tool install lanalyzer

# Using uv
uv add lanalyzer

# With MCP support
uv add lanalyzer[mcp]
```

#### Option 2: Install from Source

```bash
git clone https://github.com/bayuncao/lanalyzer.git
cd lanalyzer
uv sync
```

## 💻 Usage

### Basic Analysis

Run a taint analysis on a Python file:

```bash
lanalyzer --target <target_file> --config <config_file> --pretty --output <output_file> --log-file <log_file> --debug --minimal-output
```

### Command-Line Options

- `--target`: Path to the Python file or directory to analyze.
- `--config`: Path to the configuration file.
- `--output`: Path to save the analysis report.
- `--log-file`: Path to save the log file.
- `--pretty`: Pretty-print the output.
- `--detailed`: Show detailed analysis statistics.
- `--debug`: Enable debug mode with detailed logging.
- `--minimal-output`: (Recommended)Output only vulnerabilities and call_chains fields. Default is full output including summary and imports.

### Example

```bash
lanalyzer --target example.py --config rules/sql_injection.json --pretty --output example_analysis.json --log-file example_analysis.log --debug
```

## 🤝 Contributing

We welcome contributions! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to Lanalyzer.

For development setup, building, and publishing instructions, see [DEVELOPMENT.md](docs/DEVELOPMENT.md).

## 📄 License

This project is licensed under the GNU Affero General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## 📞 Contact

### Contact

- Issues: [GitHub Issues](https://github.com/bayuncao/lanalyzer/issues)
- Email: [8533596#gmail.com](mailto:8533596@gmail.com)

## 🧩 Model Context Protocol (MCP) Support

Lanalyzer now supports the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), allowing it to run as an MCP server that AI models and tools can use to access taint analysis functionality through a standard interface.

### Installing MCP Dependencies

If you're using pip:

```bash
pip install "lanalyzer[mcp]"
```

If you're using uv:

```bash
uv add lanalyzer[mcp]
```

### Starting the MCP Server

There are multiple ways to start the MCP server:

1. **Using Python Module**:

```bash
# View help information
python -m lanalyzer.mcp --help

# Start the server (default port 8001)
python -m lanalyzer.mcp run --port 8001 --debug
```

2. **Using the lanalyzer Command-Line Tool**:

```bash
# View help information
lanalyzer mcp --help

# Start the server (default port 8000)
lanalyzer mcp run --port 8000 --debug

# Use development mode
lanalyzer mcp dev
```

### MCP Server Features

The MCP server provides comprehensive security analysis capabilities through 8 specialized tools:

#### Core Analysis Tools

1. **`analyze_code`** - Analyze Python code strings for security vulnerabilities

   - Performs static taint analysis on provided Python source code
   - Detects SQL injection, command injection, path traversal, and other security issues
   - Returns detailed vulnerability reports with call chains and import information

2. **`analyze_file`** - Analyze individual Python files for security vulnerabilities

   - Reads and analyzes Python source files from the filesystem
   - Provides the same comprehensive analysis as `analyze_code` but for file-based input
   - Supports minimal output mode for focused vulnerability reporting

3. **`analyze_path`** - Analyze files or directories for security vulnerabilities
   - Recursively processes entire directories or single files
   - Provides comprehensive security analysis reports for projects
   - Aggregates results across multiple files with summary statistics

#### Configuration Management Tools

4. **`get_config`** - Retrieve Lanalyzer configuration content

   - Returns current configuration settings or default configuration
   - Allows examination of detection rules and analysis settings
   - Supports both file-based and default configuration retrieval

5. **`validate_config`** - Validate configuration data for correctness

   - Checks configuration structure, required fields, and data types
   - Validates both direct configuration data and configuration files
   - Returns detailed validation errors and warnings

6. **`create_config`** - Create new configuration files
   - Generates new Lanalyzer configuration files with specified settings
   - Validates configuration before creation to ensure correctness
   - Supports custom detection rules and analysis parameters

#### Report Generation Tools

7. **`explain_vulnerabilities`** - Generate natural language explanations

   - Converts technical vulnerability analysis into human-readable explanations
   - Supports both brief summaries and detailed explanations with remediation
   - Output formats: plain text or Markdown

8. **`write_vulnerability_report`** - Generate standardized vulnerability reports
   - Creates professional vulnerability reports in CVE or CNVD formats
   - Supports comprehensive vulnerability documentation with CVSS scoring
   - Includes metadata, affected products, and remediation information

For detailed MCP API documentation, see [MCP Tools Reference](docs/MCP_TOOLS.md).

### Using Lanalyzer in the MCP client

|                                          `Cursor`                                           |                                           `Augment`                                           |                                              `CherryStudio`                                              |
| :-----------------------------------------------------------------------------------------: | :-------------------------------------------------------------------------------------------: | :------------------------------------------------------------------------------------------------------: |
| <a href="https://www.youtube.com"><img src="image/cursor.png" width="120" alt="Cursor"></a> | <a href="https://www.youtube.com"><img src="image/augment.png" width="120" alt="Augment"></a> | <a href="https://www.youtube.com"><img src="image/cherry-studio.png" width="120" alt="CherryStudio"></a> |

### Integration with AI Tools

The MCP server can be integrated with AI tools that support the MCP protocol:

```python
# Using the FastMCP client
from fastmcp import FastMCPClient

# Create a client connected to the server
client = FastMCPClient("http://127.0.0.1:8000")

# Analyze code
result = client.call({
    "type": "analyze_code",
    "code": "user_input = input()\nquery = f\"SELECT * FROM users WHERE name = '{user_input}'\"",
    "file_path": "example.py",
    "config_path": "/path/to/config.json"
})

# Print analysis results
print(result)
```

### Using in Cursor

If you're working in the Cursor editor, you can directly ask the AI to use Lanalyzer to analyze your code:

```
Please use lanalyzer to analyze the current file for security vulnerabilities and explain the potential risks.
```

### MCP Command-Line Options

The MCP server supports the following command-line options:

**For `python -m lanalyzer.mcp run`**:

- `--debug`: Enable debug mode with detailed logging
- `--host`: Set the server listening address (default: 127.0.0.1)
- `--port`: Set the server listening port (default: 8001)
- `--transport`: Transport protocol (sse or streamable-http)

**For `lanalyzer mcp run`**:

- `--debug`: Enable debug mode
- `--port`: Set the server listening port (default: 8000)

### Advanced MCP Usage

#### Custom Configurations

You can use the get_config, validate_config, and create_config tools to manage vulnerability detection configurations:

```python
# Get the default configuration
config = client.call({
    "type": "get_config"
})

# Create a new configuration
result = client.call({
    "type": "create_config",
    "config_data": {...},  # Configuration data
    "config_path": "/path/to/save/config.json"  # Optional
})
```

#### Batch File Analysis

Analyze an entire project or directory:

```python
result = client.call({
    "type": "analyze_path",
    "target_path": "/path/to/project",
    "config_path": "/path/to/config.json",
    "output_path": "/path/to/output.json"  # Optional
})
```

## 📊 Analysis Results Format

>

The analysis results are returned in JSON format with the following main sections:

- **`vulnerabilities`**: List of detected security vulnerabilities
- **`call_chains`**: Data flow paths from sources to sinks
- **`summary`**: Analysis statistics and overview
- **`imports`**: Import information for analyzed files

For detailed format specification, see [Output Format Documentation](docs/OUTPUT_FORMAT.md).
