"""
F-Work MCP CLI

Command-line interface for the F-Work MCP server.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

from .server import WorkDailyReportMCPServer


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="F-Work MCP Server - Work progress tracking and daily report generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start the MCP server
  f-work-mcp

  # Start with custom transport
  f-work-mcp --transport http

  # Show version
  f-work-mcp --version

  # Show help
  f-work-mcp --help
        """
    )
    
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)"
    )
    
    parser.add_argument(
        "--host",
        default="localhost",
        help="Host for HTTP transport (default: localhost)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    try:
        # Create and run the server
        server = WorkDailyReportMCPServer()
        
        if args.debug:
            print(f"Starting F-Work MCP Server with transport: {args.transport}")
            if args.transport == "http":
                print(f"Server will be available at: http://{args.host}:{args.port}")
        
        server.run(transport=args.transport)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 