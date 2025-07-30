# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-19

### Added
- Initial release of F-Work MCP Server
- Work start/end tracking functionality
- Git integration for commit tracking
- Python file diff analysis
- Daily report generation
- MCP protocol support with tools, resources, prompts, and completions
- Command-line interface (CLI)
- Simple GUI interface
- Custom HTTP routes for health checks and statistics
- Comprehensive data structures for work state and reports
- File hashing and change detection
- Support for multiple working directories
- Automatic completion suggestions
- Professional package structure with proper Python packaging

### Features
- **Work Tracking**: Record work start and end states with comprehensive metadata
- **Git Integration**: Track commits, branch information, and file modifications
- **Python File Analysis**: Detailed diff analysis of Python files with line-by-line changes
- **Daily Reports**: Generate comprehensive daily work reports with statistics
- **MCP Protocol**: Full MCP server implementation with tools, resources, and prompts
- **Multiple Interfaces**: CLI, GUI, and programmatic access
- **Data Persistence**: JSON-based storage for work states and reports
- **Extensible Architecture**: Modular design for easy extension

### Technical Details
- Python 3.8+ compatibility
- Uses FastMCP framework
- SHA256 file hashing for change detection
- Unified diff format for code changes
- JSON-based data storage
- Comprehensive error handling
- Type hints throughout the codebase 