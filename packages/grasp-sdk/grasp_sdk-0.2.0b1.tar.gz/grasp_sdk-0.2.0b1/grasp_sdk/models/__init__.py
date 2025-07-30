"""Type definitions for Grasp SDK Python implementation.

This module contains TypedDict classes and enums that correspond to 
the TypeScript interfaces in the Node.js version.
"""

from typing import TypedDict, Optional, Dict, Any, List, Union
from typing_extensions import NotRequired
from enum import Enum


class SandboxStatus(Enum):
    """Sandbox status enumeration."""
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


class ISandboxConfig(TypedDict):
    """Sandbox configuration interface."""
    key: str  # Required: Grasp API key
    timeout: int  # Required: Default timeout in milliseconds
    workspace: NotRequired[str]  # Optional: Grasp workspace ID
    debug: NotRequired[bool]  # Optional: Enable debug mode for detailed logging
    keepAliveMs: NotRequired[int]  # Optional: Keep-alive time in milliseconds
    

class IBrowserConfig(TypedDict):
    """Browser service configuration interface."""
    args: List[str]  # Required: Chromium launch arguments
    headless: bool  # Required: Headless mode (default: true)
    launchTimeout: int  # Required: Timeout for browser launch (default: 30000ms)
    envs: Dict[str, str]  # Required: The environment variables


class ICommandOptions(TypedDict):
    """Command execution options interface."""
    inBackground: NotRequired[bool]  # Whether to run command in background (corresponds to 'background' in TypeScript)
    timeout_ms: NotRequired[int]  # Timeout in milliseconds (corresponds to 'timeoutMs' in TypeScript)
    cwd: NotRequired[str]  # Working directory
    user: NotRequired[str]  # User to run the command as (default: 'user')
    envs: NotRequired[Dict[str, str]]  # Environment variables for the command
    nohup: NotRequired[bool]  # Whether to use nohup for command execution (Grasp-specific extension)
    # Note: onStdout and onStderr callbacks are handled differently in Python implementation
    

class IScriptOptions(TypedDict):
    """Script execution options interface."""
    type: str  # Required: Script type: 'cjs' for CommonJS, 'esm' for ES Modules, 'py' for Python
    cwd: NotRequired[str]  # Working directory
    timeout_ms: NotRequired[int]  # Timeout in milliseconds
    background: NotRequired[bool]  # Run in background
    user: NotRequired[str]  # User to run the script as (default: 'user')
    nohup: NotRequired[bool]  # Use nohup for background execution (Grasp-specific extension)
    envs: NotRequired[Dict[str, str]]  # The environment variables
    preCommand: NotRequired[str]  # Pre command


class ILoggerConfig(TypedDict):
    """Logger configuration interface."""
    level: str  # Required: Log level ('debug' | 'info' | 'warn' | 'error')
    console: bool  # Required: Enable console output
    file: NotRequired[str]  # Optional: Log file path


class IAppConfig(TypedDict):
    """Application configuration interface."""
    sandbox: ISandboxConfig  # Required: E2B configuration
    logger: ILoggerConfig  # Required: Logger configuration


__all__ = [
    'SandboxStatus',
    'ISandboxConfig',
    'IBrowserConfig',
    'ICommandOptions',
    'IScriptOptions',
    'ILoggerConfig',
    'IAppConfig',
]