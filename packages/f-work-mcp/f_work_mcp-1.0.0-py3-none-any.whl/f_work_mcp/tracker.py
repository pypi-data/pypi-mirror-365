"""
F-Work MCP Tracker

This module contains the core tracking logic and data structures for work progress monitoring.
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


@dataclass
class PythonFileContent:
    """Python文件内容结构"""
    file_path: str
    content: str
    hash: str
    lines_count: int
    last_modified: str


@dataclass
class FileDiff:
    """文件差异结构"""
    file_path: str
    diff_type: str  # 'modified', 'added', 'deleted'
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    diff_lines: List[str] = None
    added_lines: int = 0
    deleted_lines: int = 0
    changed_lines: int = 0


@dataclass
class WorkState:
    """工作状态数据结构"""
    timestamp: str
    git_status: str
    git_commits: List[Dict[str, str]]
    file_hashes: Dict[str, str]
    python_files: Dict[str, PythonFileContent]
    working_directory: str
    branch_name: str
    total_files: int
    modified_files: List[str]


@dataclass
class DailyReport:
    """日报数据结构"""
    date: str
    work_start_time: str
    work_end_time: str
    working_hours: float
    total_commits: int
    modified_files: List[str]
    new_files: List[str]
    deleted_files: List[str]
    python_file_diffs: List[FileDiff]
    commit_summary: List[Dict[str, str]]
    work_summary: str
    code_changes_summary: str


class WorkTracker:
    """工作跟踪器"""
    
    def __init__(self, data_dir: str = ".work_tracker"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.state_file = self.data_dir / "work_states.json"
        self.reports_dir = self.data_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def get_git_status(self, working_dir: str) -> str:
        """获取Git状态"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""
    
    def get_git_commits(self, working_dir: str, since: Optional[str] = None) -> List[Dict[str, str]]:
        """获取Git提交记录"""
        try:
            cmd = ["git", "log", "--pretty=format:%H|%an|%ad|%s", "--date=iso"]
            if since:
                cmd.extend(["--since", since])
            
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "date": parts[2],
                            "message": parts[3]
                        })
            return commits
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
    
    def get_branch_name(self, working_dir: str) -> str:
        """获取当前分支名"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "unknown"
    
    def get_file_hashes(self, working_dir: str) -> Dict[str, str]:
        """获取所有文件的哈希值"""
        file_hashes = {}
        working_path = Path(working_dir)
        
        # 忽略的文件和目录
        ignore_patterns = {
            '.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
            'node_modules', '.DS_Store', '*.pyc', '*.log', '.work_tracker'
        }
        
        for root, dirs, files in os.walk(working_dir):
            # 过滤掉忽略的目录
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            for file in files:
                # 过滤掉忽略的文件
                if any(pattern in file for pattern in ignore_patterns):
                    continue
                
                file_path = Path(root) / file
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    # 使用相对路径作为键
                    relative_path = str(file_path.relative_to(working_path))
                    file_hashes[relative_path] = file_hash
                except (IOError, OSError):
                    continue
        
        return file_hashes
    
    def get_python_files_content(self, working_dir: str) -> Dict[str, PythonFileContent]:
        """获取所有Python文件的内容"""
        python_files = {}
        working_path = Path(working_dir)
        
        # 忽略的目录
        ignore_dirs = {
            '.git', '__pycache__', '.pytest_cache', '.venv', 'venv',
            'node_modules', '.work_tracker'
        }
        
        for root, dirs, files in os.walk(working_dir):
            # 过滤掉忽略的目录
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 计算文件哈希
                        file_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
                        
                        # 获取文件修改时间
                        stat = file_path.stat()
                        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        
                        # 使用相对路径作为键
                        relative_path = str(file_path.relative_to(working_path))
                        
                        python_files[relative_path] = PythonFileContent(
                            file_path=relative_path,
                            content=content,
                            hash=file_hash,
                            lines_count=len(content.splitlines()),
                            last_modified=last_modified
                        )
                    except (IOError, OSError, UnicodeDecodeError):
                        continue
        
        return python_files
    
    def get_modified_files(self, working_dir: str) -> List[str]:
        """获取修改的文件列表"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=working_dir,
                capture_output=True,
                text=True,
                check=True
            )
            
            modified_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    status = line[:2].strip()
                    file_path = line[3:]
                    if status in ['M', 'A', 'D', 'R']:
                        modified_files.append(file_path)
            
            return modified_files
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
    
    def compare_python_files(self, start_state: WorkState, end_state: WorkState) -> List[FileDiff]:
        """比较Python文件的差异"""
        diffs = []
        
        start_files = set(start_state.python_files.keys())
        end_files = set(end_state.python_files.keys())
        
        # 新增的文件
        for file_path in end_files - start_files:
            new_content = end_state.python_files[file_path]
            diffs.append(FileDiff(
                file_path=file_path,
                diff_type='added',
                new_content=new_content.content,
                diff_lines=[f"+ {line}" for line in new_content.content.splitlines()],
                added_lines=new_content.lines_count,
                deleted_lines=0,
                changed_lines=new_content.lines_count
            ))
        
        # 删除的文件
        for file_path in start_files - end_files:
            old_content = start_state.python_files[file_path]
            diffs.append(FileDiff(
                file_path=file_path,
                diff_type='deleted',
                old_content=old_content.content,
                diff_lines=[f"- {line}" for line in old_content.content.splitlines()],
                added_lines=0,
                deleted_lines=old_content.lines_count,
                changed_lines=old_content.lines_count
            ))
        
        # 修改的文件
        for file_path in start_files & end_files:
            start_content = start_state.python_files[file_path]
            end_content = end_state.python_files[file_path]
            
            if start_content.hash != end_content.hash:
                # 生成差异
                diff_lines = list(difflib.unified_diff(
                    start_content.content.splitlines(keepends=True),
                    end_content.content.splitlines(keepends=True),
                    fromfile=f'a/{file_path}',
                    tofile=f'b/{file_path}',
                    lineterm=''
                ))
                
                # 统计变更行数
                added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
                deleted_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
                
                diffs.append(FileDiff(
                    file_path=file_path,
                    diff_type='modified',
                    old_content=start_content.content,
                    new_content=end_content.content,
                    diff_lines=diff_lines,
                    added_lines=added_lines,
                    deleted_lines=deleted_lines,
                    changed_lines=added_lines + deleted_lines
                ))
        
        return diffs
    
    def save_work_state(self, state: WorkState) -> None:
        """保存工作状态"""
        states = self.load_work_states()
        
        # 转换Python文件内容为可序列化的格式
        state_dict = asdict(state)
        # Python文件内容可能很大，可以选择性保存
        if 'python_files' in state_dict:
            # 只保存文件哈希和基本信息，不保存完整内容
            python_files_info = {}
            for file_path, file_content in state.python_files.items():
                python_files_info[file_path] = {
                    'hash': file_content.hash,
                    'lines_count': file_content.lines_count,
                    'last_modified': file_content.last_modified
                }
            state_dict['python_files_info'] = python_files_info
            del state_dict['python_files']
        
        states[state.timestamp] = state_dict
        
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(states, f, ensure_ascii=False, indent=2)
    
    def load_work_states(self) -> Dict[str, Any]:
        """加载工作状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}
    
    def get_today_states(self) -> Dict[str, WorkState]:
        """获取今天的工作状态"""
        states = self.load_work_states()
        today = datetime.now().date()
        today_states = {}
        
        for timestamp, state_data in states.items():
            state_date = datetime.fromisoformat(timestamp).date()
            if state_date == today:
                # 重新构建WorkState对象
                if 'python_files_info' in state_data:
                    # 如果有Python文件信息，需要重新获取完整内容
                    working_dir = state_data.get('working_directory', '.')
                    python_files = self.get_python_files_content(working_dir)
                    state_data['python_files'] = python_files
                    del state_data['python_files_info']
                
                today_states[timestamp] = WorkState(**state_data)
        
        return today_states
    
    def generate_daily_report(self, start_state: WorkState, end_state: WorkState) -> DailyReport:
        """生成日报"""
        start_time = datetime.fromisoformat(start_state.timestamp)
        end_time = datetime.fromisoformat(end_state.timestamp)
        working_hours = (end_time - start_time).total_seconds() / 3600
        
        # 比较文件变化
        start_files = set(start_state.file_hashes.keys())
        end_files = set(end_state.file_hashes.keys())
        
        new_files = list(end_files - start_files)
        deleted_files = list(start_files - end_files)
        
        # 找出修改的文件
        modified_files = []
        for file in start_files & end_files:
            if start_state.file_hashes[file] != end_state.file_hashes[file]:
                modified_files.append(file)
        
        # 获取Python文件差异
        python_file_diffs = self.compare_python_files(start_state, end_state)
        
        # 获取提交记录
        commits_since_start = self.get_git_commits(
            end_state.working_directory,
            since=start_state.timestamp
        )
        
        # 生成工作摘要
        work_summary = self._generate_work_summary(
            modified_files, new_files, deleted_files, commits_since_start
        )
        
        # 生成代码变更摘要
        code_changes_summary = self._generate_code_changes_summary(python_file_diffs)
        
        return DailyReport(
            date=start_time.strftime("%Y-%m-%d"),
            work_start_time=start_time.strftime("%H:%M"),
            work_end_time=end_time.strftime("%H:%M"),
            working_hours=round(working_hours, 2),
            total_commits=len(commits_since_start),
            modified_files=modified_files,
            new_files=new_files,
            deleted_files=deleted_files,
            python_file_diffs=python_file_diffs,
            commit_summary=commits_since_start,
            work_summary=work_summary,
            code_changes_summary=code_changes_summary
        )
    
    def _generate_work_summary(self, modified_files: List[str], new_files: List[str], 
                              deleted_files: List[str], commits: List[Dict[str, str]]) -> str:
        """生成工作摘要"""
        summary_parts = []
        
        if commits:
            summary_parts.append(f"完成了 {len(commits)} 次代码提交")
        
        if modified_files:
            summary_parts.append(f"修改了 {len(modified_files)} 个文件")
        
        if new_files:
            summary_parts.append(f"新增了 {len(new_files)} 个文件")
        
        if deleted_files:
            summary_parts.append(f"删除了 {len(deleted_files)} 个文件")
        
        if not summary_parts:
            summary_parts.append("今天没有代码变更")
        
        return "，".join(summary_parts) + "。"
    
    def _generate_code_changes_summary(self, python_file_diffs: List[FileDiff]) -> str:
        """生成代码变更摘要"""
        if not python_file_diffs:
            return "没有Python文件变更。"
        
        summary_parts = []
        total_added = 0
        total_deleted = 0
        total_modified = 0
        
        for diff in python_file_diffs:
            if diff.diff_type == 'added':
                summary_parts.append(f"新增文件 {diff.file_path} ({diff.added_lines} 行)")
                total_added += diff.added_lines
            elif diff.diff_type == 'deleted':
                summary_parts.append(f"删除文件 {diff.file_path} ({diff.deleted_lines} 行)")
                total_deleted += diff.deleted_lines
            elif diff.diff_type == 'modified':
                summary_parts.append(f"修改文件 {diff.file_path} (+{diff.added_lines} -{diff.deleted_lines} 行)")
                total_added += diff.added_lines
                total_deleted += diff.deleted_lines
                total_modified += 1
        
        summary = f"Python代码变更: {', '.join(summary_parts)}。"
        summary += f" 总计: +{total_added} -{total_deleted} 行代码。"
        
        return summary
    
    def save_daily_report(self, report: DailyReport) -> str:
        """保存日报"""
        report_filename = f"daily_report_{report.date}.json"
        report_path = self.reports_dir / report_filename
        
        # 转换FileDiff对象为可序列化的格式
        report_dict = asdict(report)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        return str(report_path) 