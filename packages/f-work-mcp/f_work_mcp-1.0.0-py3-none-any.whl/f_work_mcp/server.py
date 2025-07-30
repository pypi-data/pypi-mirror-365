"""
F-Work MCP Server

This module contains the main MCP server implementation for work tracking and daily report generation.
"""

import json
import os
import hashlib
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import difflib

from mcp.server.fastmcp import FastMCP
from mcp.types import Completion, CompletionArgument, CompletionContext
from mcp.types import PromptReference, ResourceTemplateReference
from starlette.requests import Request
from starlette.responses import JSONResponse

from .tracker import WorkTracker, WorkState, DailyReport, PythonFileContent, FileDiff


class WorkDailyReportMCPServer:
    """F-Work MCP Server for tracking work progress and generating daily reports."""
    
    def __init__(self, name: str = "F-Work MCP Server"):
        self.mcp = FastMCP(name)
        self.work_tracker = WorkTracker()
        self._setup_tools()
        self._setup_resources()
        self._setup_prompts()
        self._setup_completions()
        self._setup_routes()
    
    def _setup_tools(self):
        """Setup MCP tools."""
        
        @self.mcp.tool()
        def work_start(working_directory: str = ".") -> Dict[str, Any]:
            """
            记录工作开始状态
            
            Args:
                working_directory: 工作目录路径，默认为当前目录
                
            Returns:
                包含工作开始状态信息的字典
            """
            try:
                # 获取当前工作目录的绝对路径
                working_dir = os.path.abspath(working_directory)
                
                # 检查目录是否存在
                if not os.path.exists(working_dir):
                    return {
                        "success": False,
                        "error": f"工作目录不存在: {working_dir}"
                    }
                
                # 获取各种状态信息
                git_status = self.work_tracker.get_git_status(working_dir)
                git_commits = self.work_tracker.get_git_commits(working_dir)
                file_hashes = self.work_tracker.get_file_hashes(working_dir)
                python_files = self.work_tracker.get_python_files_content(working_dir)
                branch_name = self.work_tracker.get_branch_name(working_dir)
                modified_files = self.work_tracker.get_modified_files(working_dir)
                
                # 创建工作状态
                work_state = WorkState(
                    timestamp=datetime.now().isoformat(),
                    git_status=git_status,
                    git_commits=git_commits,
                    file_hashes=file_hashes,
                    python_files=python_files,
                    working_directory=working_dir,
                    branch_name=branch_name,
                    total_files=len(file_hashes),
                    modified_files=modified_files
                )
                
                # 保存状态
                self.work_tracker.save_work_state(work_state)
                
                return {
                    "success": True,
                    "message": "工作开始状态已记录",
                    "timestamp": work_state.timestamp,
                    "working_directory": working_dir,
                    "branch_name": branch_name,
                    "total_files": work_state.total_files,
                    "modified_files_count": len(modified_files),
                    "git_commits_count": len(git_commits),
                    "python_files_count": len(python_files)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"记录工作开始状态时出错: {str(e)}"
                }
        
        @self.mcp.tool()
        def work_end(working_directory: str = ".") -> Dict[str, Any]:
            """
            记录工作结束状态并生成日报
            
            Args:
                working_directory: 工作目录路径，默认为当前目录
                
            Returns:
                包含日报信息的字典
            """
            try:
                # 获取当前工作目录的绝对路径
                working_dir = os.path.abspath(working_directory)
                
                # 检查目录是否存在
                if not os.path.exists(working_dir):
                    return {
                        "success": False,
                        "error": f"工作目录不存在: {working_dir}"
                    }
                
                # 获取今天的工作状态
                today_states = self.work_tracker.get_today_states()
                
                if not today_states:
                    return {
                        "success": False,
                        "error": "今天没有找到工作开始记录，请先运行 work_start"
                    }
                
                # 获取最早的工作开始状态
                start_timestamp = min(today_states.keys())
                start_state = today_states[start_timestamp]
                
                # 获取当前状态
                current_git_status = self.work_tracker.get_git_status(working_dir)
                current_git_commits = self.work_tracker.get_git_commits(working_dir)
                current_file_hashes = self.work_tracker.get_file_hashes(working_dir)
                current_python_files = self.work_tracker.get_python_files_content(working_dir)
                current_branch_name = self.work_tracker.get_branch_name(working_dir)
                current_modified_files = self.work_tracker.get_modified_files(working_dir)
                
                end_state = WorkState(
                    timestamp=datetime.now().isoformat(),
                    git_status=current_git_status,
                    git_commits=current_git_commits,
                    file_hashes=current_file_hashes,
                    python_files=current_python_files,
                    working_directory=working_dir,
                    branch_name=current_branch_name,
                    total_files=len(current_file_hashes),
                    modified_files=current_modified_files
                )
                
                # 生成日报
                daily_report = self.work_tracker.generate_daily_report(start_state, end_state)
                
                # 保存日报
                report_path = self.work_tracker.save_daily_report(daily_report)
                
                # 保存结束状态
                self.work_tracker.save_work_state(end_state)
                
                # 准备返回的Python文件差异信息
                python_diffs_summary = []
                for diff in daily_report.python_file_diffs:
                    diff_summary = {
                        "file_path": diff.file_path,
                        "diff_type": diff.diff_type,
                        "added_lines": diff.added_lines,
                        "deleted_lines": diff.deleted_lines,
                        "changed_lines": diff.changed_lines
                    }
                    if diff.diff_lines:
                        # 只返回前10行差异，避免响应过大
                        diff_summary["diff_preview"] = diff.diff_lines[:10]
                    python_diffs_summary.append(diff_summary)
                
                return {
                    "success": True,
                    "message": "工作结束状态已记录，日报已生成",
                    "report": {
                        "date": daily_report.date,
                        "work_start_time": daily_report.work_start_time,
                        "work_end_time": daily_report.work_end_time,
                        "working_hours": daily_report.working_hours,
                        "total_commits": daily_report.total_commits,
                        "modified_files_count": len(daily_report.modified_files),
                        "new_files_count": len(daily_report.new_files),
                        "deleted_files_count": len(daily_report.deleted_files),
                        "work_summary": daily_report.work_summary,
                        "code_changes_summary": daily_report.code_changes_summary,
                        "report_path": report_path
                    },
                    "details": {
                        "modified_files": daily_report.modified_files,
                        "new_files": daily_report.new_files,
                        "deleted_files": daily_report.deleted_files,
                        "commits": daily_report.commit_summary,
                        "python_file_diffs": python_diffs_summary
                    }
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"记录工作结束状态时出错: {str(e)}"
                }
        
        @self.mcp.tool()
        def get_work_status(working_directory: str = ".") -> Dict[str, Any]:
            """
            获取当前工作状态
            
            Args:
                working_directory: 工作目录路径，默认为当前目录
                
            Returns:
                包含当前工作状态信息的字典
            """
            try:
                working_dir = os.path.abspath(working_directory)
                
                if not os.path.exists(working_dir):
                    return {
                        "success": False,
                        "error": f"工作目录不存在: {working_dir}"
                    }
                
                # 获取当前状态
                git_status = self.work_tracker.get_git_status(working_dir)
                git_commits = self.work_tracker.get_git_commits(working_dir)
                file_hashes = self.work_tracker.get_file_hashes(working_dir)
                python_files = self.work_tracker.get_python_files_content(working_dir)
                branch_name = self.work_tracker.get_branch_name(working_dir)
                modified_files = self.work_tracker.get_modified_files(working_dir)
                
                # 获取今天的工作状态
                today_states = self.work_tracker.get_today_states()
                
                return {
                    "success": True,
                    "current_time": datetime.now().isoformat(),
                    "working_directory": working_dir,
                    "branch_name": branch_name,
                    "total_files": len(file_hashes),
                    "modified_files": modified_files,
                    "modified_files_count": len(modified_files),
                    "git_commits_count": len(git_commits),
                    "python_files_count": len(python_files),
                    "today_work_sessions": len(today_states),
                    "has_work_start": len(today_states) > 0
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"获取工作状态时出错: {str(e)}"
                }
        
        @self.mcp.tool()
        def get_daily_report(date: str = None) -> Dict[str, Any]:
            """
            获取指定日期的日报
            
            Args:
                date: 日期格式 YYYY-MM-DD，默认为今天
                
            Returns:
                包含日报信息的字典
            """
            try:
                if date is None:
                    date = datetime.now().strftime("%Y-%m-%d")
                
                report_filename = f"daily_report_{date}.json"
                report_path = self.work_tracker.reports_dir / report_filename
                
                if not report_path.exists():
                    return {
                        "success": False,
                        "error": f"未找到 {date} 的日报"
                    }
                
                with open(report_path, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                return {
                    "success": True,
                    "date": date,
                    "report": report_data
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"获取日报时出错: {str(e)}"
                }
        
        @self.mcp.tool()
        def get_python_file_diff(file_path: str, working_directory: str = ".") -> Dict[str, Any]:
            """
            获取指定Python文件的详细差异信息
            
            Args:
                file_path: Python文件路径
                working_directory: 工作目录路径，默认为当前目录
                
            Returns:
                包含文件差异信息的字典
            """
            try:
                working_dir = os.path.abspath(working_directory)
                
                if not os.path.exists(working_dir):
                    return {
                        "success": False,
                        "error": f"工作目录不存在: {working_dir}"
                    }
                
                # 获取今天的工作状态
                today_states = self.work_tracker.get_today_states()
                
                if not today_states:
                    return {
                        "success": False,
                        "error": "今天没有找到工作开始记录，请先运行 work_start"
                    }
                
                # 获取最早的工作开始状态
                start_timestamp = min(today_states.keys())
                start_state = today_states[start_timestamp]
                
                # 获取当前状态
                current_python_files = self.work_tracker.get_python_files_content(working_dir)
                
                # 检查文件是否存在
                if file_path not in start_state.python_files and file_path not in current_python_files:
                    return {
                        "success": False,
                        "error": f"文件 {file_path} 不存在"
                    }
                
                # 生成差异
                diffs = self.work_tracker.compare_python_files(start_state, WorkState(
                    timestamp=datetime.now().isoformat(),
                    git_status="",
                    git_commits=[],
                    file_hashes={},
                    python_files=current_python_files,
                    working_directory=working_dir,
                    branch_name="",
                    total_files=0,
                    modified_files=[]
                ))
                
                # 查找指定文件的差异
                file_diff = None
                for diff in diffs:
                    if diff.file_path == file_path:
                        file_diff = diff
                        break
                
                if not file_diff:
                    return {
                        "success": True,
                        "message": f"文件 {file_path} 没有变更",
                        "file_path": file_path,
                        "diff_type": "no_change"
                    }
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "diff_type": file_diff.diff_type,
                    "added_lines": file_diff.added_lines,
                    "deleted_lines": file_diff.deleted_lines,
                    "changed_lines": file_diff.changed_lines,
                    "diff_lines": file_diff.diff_lines,
                    "old_content": file_diff.old_content,
                    "new_content": file_diff.new_content
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"获取文件差异时出错: {str(e)}"
                }
    
    def _setup_resources(self):
        """Setup MCP resources."""
        
        @self.mcp.resource("work-status://{working_directory}")
        def get_work_status_resource(working_directory: str = ".") -> str:
            """获取工作状态资源"""
            status = get_work_status(working_directory)
            return json.dumps(status, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("daily-report://{date}")
        def get_daily_report_resource(date: str) -> str:
            """获取日报资源"""
            report = get_daily_report(date)
            return json.dumps(report, ensure_ascii=False, indent=2)
        
        @self.mcp.resource("python-diff://{file_path}")
        def get_python_diff_resource(file_path: str) -> str:
            """获取Python文件差异资源"""
            diff = get_python_file_diff(file_path)
            return json.dumps(diff, ensure_ascii=False, indent=2)
    
    def _setup_prompts(self):
        """Setup MCP prompts."""
        
        @self.mcp.prompt()
        def generate_work_summary_prompt(working_directory: str = ".", style: str = "professional") -> str:
            """生成工作摘要提示词"""
            styles = {
                "professional": "请以专业的语气",
                "casual": "请以轻松的语气",
                "detailed": "请详细描述"
            }
            
            return f"{styles.get(style, styles['professional'])}总结在 {working_directory} 目录下的工作内容，包括代码变更、提交记录和工作时长等信息。重点关注Python文件的修改内容，分析代码逻辑的变化。"
    
    def _setup_completions(self):
        """Setup MCP completions."""
        
        @self.mcp.completion()
        async def handle_work_directory_completion(ref, argument: CompletionArgument, context: CompletionContext):
            """为工作目录提供补全建议"""
            if argument.name == "working_directory":
                # 返回常见的项目目录
                common_dirs = [".", "..", "./src", "./app", "./frontend", "./backend"]
                return Completion(values=common_dirs)
            return None
        
        @self.mcp.completion()
        async def handle_date_completion(ref, argument: CompletionArgument, context: CompletionContext):
            """为日期提供补全建议"""
            if argument.name == "date":
                # 返回最近几天的日期
                dates = []
                for i in range(7):
                    date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                    dates.append(date)
                return Completion(values=dates)
            return None
        
        @self.mcp.completion()
        async def handle_python_file_completion(ref, argument: CompletionArgument, context: CompletionContext):
            """为Python文件路径提供补全建议"""
            if argument.name == "file_path":
                # 返回当前目录下的Python文件
                python_files = []
                for root, dirs, files in os.walk('.'):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            python_files.append(file_path)
                return Completion(values=python_files[:10])  # 限制数量
            return None
    
    def _setup_routes(self):
        """Setup custom HTTP routes."""
        
        @self.mcp.custom_route("/health", methods=["GET"])
        async def health_check(request: Request) -> JSONResponse:
            """健康检查端点"""
            return JSONResponse({
                "status": "ok",
                "service": "F-Work MCP Server",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.mcp.custom_route("/stats", methods=["GET"])
        async def get_stats(request: Request) -> JSONResponse:
            """获取服务器统计信息"""
            try:
                today_states = self.work_tracker.get_today_states()
                reports_count = len(list(self.work_tracker.reports_dir.glob("daily_report_*.json")))
                
                return JSONResponse({
                    "today_work_sessions": len(today_states),
                    "total_reports": reports_count,
                    "data_directory": str(self.work_tracker.data_dir),
                    "server_start_time": datetime.now().isoformat()
                })
            except Exception as e:
                return JSONResponse({
                    "error": str(e)
                }, status_code=500)
    
    def run(self, transport: str = "stdio"):
        """运行MCP服务器"""
        self.mcp.run(transport=transport)
    
    def get_mcp_server(self) -> FastMCP:
        """获取MCP服务器实例"""
        return self.mcp 