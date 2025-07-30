"""
F-Work MCP Server

A MCP server for tracking work progress and generating daily reports with Python file diff analysis.
"""

__version__ = "1.0.0"
__author__ = "F-Work MCP Team"
__email__ = "contact@f-work-mcp.com"

from .server import WorkDailyReportMCPServer
from .tracker import WorkTracker, WorkState, DailyReport, PythonFileContent, FileDiff

__all__ = [
    "WorkDailyReportMCPServer",
    "WorkTracker",
    "WorkState", 
    "DailyReport",
    "PythonFileContent",
    "FileDiff",
    "__version__",
] 