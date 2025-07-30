"""
Security manager for AI Helper Agent
"""

import os
import pathlib
from typing import List, Dict, Any, Set
import structlog

logger = structlog.get_logger()


class SecurityManager:
    """Manages security policies and access control"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = pathlib.Path(workspace_path).resolve()
        self.allowed_extensions = {".py", ".txt", ".md", ".json", ".yaml", ".yml", ".toml"}
        self.blocked_paths = {
            "/etc", "/bin", "/usr/bin", "/sbin", "/usr/sbin",
            "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"
        }
        self.blocked_patterns = {
            "password", "secret", "token", "key", "credential",
            ".ssh", ".git/config", "database.yml", ".env"
        }
    
    def is_file_accessible(self, filepath: str) -> bool:
        """Check if file is accessible for read/write operations"""
        try:
            file_path = pathlib.Path(filepath).resolve()
            
            # Check if file is within workspace
            try:
                file_path.relative_to(self.workspace_path)
            except ValueError:
                logger.warning("File access denied: outside workspace", 
                             file=str(file_path), workspace=str(self.workspace_path))
                return False
            
            # Check blocked paths
            file_str = str(file_path).lower()
            for blocked in self.blocked_paths:
                if file_str.startswith(blocked.lower()):
                    logger.warning("File access denied: blocked path", file=str(file_path))
                    return False
            
            # Check blocked patterns
            for pattern in self.blocked_patterns:
                if pattern.lower() in file_str:
                    logger.warning("File access denied: contains blocked pattern", 
                                 file=str(file_path), pattern=pattern)
                    return False
            
            # Check file extension
            if file_path.suffix.lower() not in self.allowed_extensions:
                logger.warning("File access denied: unsupported extension", 
                             file=str(file_path), extension=file_path.suffix)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Error checking file access", error=str(e), file=filepath)
            return False
    
    def validate_command(self, command: str) -> bool:
        """Validate if a command is safe to execute"""
        dangerous_commands = {
            "rm", "del", "rmdir", "format", "fdisk", "mkfs",
            "sudo", "su", "chmod", "chown", "passwd",
            "wget", "curl", "nc", "netcat", "telnet",
            "python -c", "exec", "eval"
        }
        
        command_lower = command.lower().strip()
        
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                logger.warning("Command blocked: contains dangerous pattern", 
                             command=command, pattern=dangerous)
                return False
        
        return True
    
    def authorize_task(self, task_description: str) -> bool:
        """Authorize a task based on its description"""
        # Simple authorization - can be extended
        sensitive_operations = [
            "delete", "remove", "format", "install", "uninstall",
            "network", "internet", "download", "upload", "send"
        ]
        
        desc_lower = task_description.lower()
        for operation in sensitive_operations:
            if operation in desc_lower:
                logger.info("Sensitive operation detected, requiring approval", 
                          task=task_description, operation=operation)
                return self._request_user_approval(task_description)
        
        return True
    
    def _request_user_approval(self, task: str) -> bool:
        """Request user approval for sensitive operations"""
        try:
            response = input(f"\n⚠️  The agent wants to perform: {task}\nDo you approve? (y/N): ")
            approved = response.lower().strip() == 'y'
            logger.info("User approval requested", task=task, approved=approved)
            return approved
        except (KeyboardInterrupt, EOFError):
            logger.info("User approval cancelled")
            return False
    
    def get_safe_temp_dir(self) -> pathlib.Path:
        """Get a safe temporary directory for operations"""
        import tempfile
        temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="ai_helper_"))
        logger.debug("Created safe temp directory", path=str(temp_dir))
        return temp_dir


# Global security manager instance
security_manager = SecurityManager()
