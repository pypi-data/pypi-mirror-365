#!/usr/bin/env python3
"""
MCP Server for stateful Jupyter kernel development
Provides tools for executing Python code with persistent state
"""

import json
import sys
import typing as t
from datetime import datetime
from typing import Any, Dict, Annotated, Literal, Optional
from dataclasses import dataclass

from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Dictionary to store multiple kernels
kernels = {}  # kernel_id -> {'manager': KernelManager, 'client': KernelClient, 'created_at': datetime, 'language': str, 'env_path': str}

import uuid
import subprocess
import os

# Structured return types for better Claude Code display
@dataclass
class KernelInfo:
    kernel_id: str
    success: bool
    message: str
    timestamp: str
    error: Optional[str] = None

@dataclass
class ExecutionResult:
    success: bool
    output: list[str]
    result: Optional[str]
    error: Optional[dict]
    timestamp: str

@dataclass
class KernelStatus:
    kernel_id: str
    status: str
    created_at: str
    language: str
    env_path: str
    details: Optional[dict] = None

@dataclass
class KernelList:
    success: bool
    kernels: dict[str, dict]
    count: int
    timestamp: str

@dataclass
class VariableInfo:
    name: str
    type: str
    repr: str
    size: int

@dataclass
class VariableList:
    success: bool
    variables: dict[str, VariableInfo]
    count: int
    timestamp: str
    kernel_id: str

def validate_python_environment(python_path):
    """Validate that Python environment has required packages"""
    try:
        # Check if ipykernel is available
        result = subprocess.run(
            [python_path, "-c", "import ipykernel"],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise ValueError(
                f"ipykernel not found in Python environment: {python_path}\n"
                f"Please install ipykernel in your Python environment. Examples:\n"
                f"  pip install ipykernel\n"
                f"  conda install ipykernel\n"
                f"  poetry add ipykernel\n"
                f"  uv add ipykernel"
            )
            
    except subprocess.TimeoutExpired:
        raise ValueError(f"Timeout checking Python environment: {python_path}")
    except FileNotFoundError:
        raise ValueError(f"Python executable not found: {python_path}")

def validate_node_environment(node_path):
    """Validate that Node.js environment has TSLAB installed"""
    try:
        # Check Node.js version
        result = subprocess.run(
            [node_path, "--version"],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise ValueError(f"Node.js executable not working: {node_path}")
            
        # Check if tslab is available globally
        result = subprocess.run(
            ["tslab", "install", "--version"],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            raise ValueError(
                f"tslab not found or not properly installed\n"
                f"Please install tslab globally. Examples:\n"
                f"  npm install -g tslab\n"
                f"  tslab install\n"
                f"Then verify with: jupyter kernelspec list"
            )
        
        # Check if tslab kernelspecs are installed
        result = subprocess.run(
            ["jupyter", "kernelspec", "list", "--json"],
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            import json
            kernelspecs = json.loads(result.stdout.decode())
            available_kernels = kernelspecs.get('kernelspecs', {}).keys()
            if 'tslab' not in available_kernels:
                raise ValueError(
                    f"tslab kernel not found in Jupyter kernelspecs\n"
                    f"Please run: tslab install\n"
                    f"Available kernels: {list(available_kernels)}"
                )
            
    except subprocess.TimeoutExpired:
        raise ValueError(f"Timeout checking Node.js environment: {node_path}")
    except FileNotFoundError as e:
        if "tslab" in str(e):
            raise ValueError(
                f"tslab command not found\n"
                f"Please install tslab globally: npm install -g tslab"
            )
        elif "jupyter" in str(e):
            raise ValueError(
                f"jupyter command not found\n"
                f"Please install Jupyter: pip install jupyter"
            )
        else:
            raise ValueError(f"Node.js executable not found: {node_path}")

def validate_environment(language, env_path):
    """Validate environment based on language type"""
    if language == "python":
        validate_python_environment(env_path)
    elif language in ["typescript", "javascript"]:
        validate_node_environment(env_path)
    else:
        raise ValueError(f"Unsupported language: {language}")

def create_kernel(language, env_path, kernel_id=None):
    """Create a new Jupyter kernel for the specified language"""
    if kernel_id is None:
        kernel_id = str(uuid.uuid4())[:8]  # Short ID
    
    if kernel_id in kernels:
        raise ValueError(f"Kernel {kernel_id} already exists")
    
    print(f"Starting {language} kernel {kernel_id} with environment: {env_path}")
    
    # Validate environment exists and is executable
    if not os.path.exists(env_path):
        raise ValueError(f"Executable not found: {env_path}")
    if not os.access(env_path, os.X_OK):
        raise ValueError(f"Executable not executable: {env_path}")
    
    # Validate environment has required packages
    validate_environment(language, env_path)
    
    if language == "python":
        km = create_python_kernel(env_path)
    elif language == "typescript":
        km = create_tslab_kernel("tslab")
    elif language == "javascript":
        km = create_tslab_kernel("jslab")
    else:
        raise ValueError(f"Unsupported language: {language}")
    
    # Start kernel and get client
    km.start_kernel()
    kc = km.client()
    kc.wait_for_ready()
    
    kernels[kernel_id] = {
        'manager': km,
        'client': kc, 
        'created_at': datetime.now(),
        'language': language,
        'env_path': env_path
    }
    
    print(f"{language.title()} kernel {kernel_id} ready!")
    return kernel_id

def create_python_kernel(python_env):
    """Create a Python kernel with custom environment"""
    class CustomKernelManager(KernelManager):
        """Custom KernelManager that preserves specified Python executable"""
        
        def __init__(self, custom_python_path: str, **kwargs):
            self.custom_python_path = custom_python_path
            super().__init__(**kwargs)
        
        def format_kernel_cmd(self, extra_arguments: t.Optional[t.List[str]] = None) -> t.List[str]:
            """Override to preserve our custom Python path"""
            # Get the normal formatted command from parent
            cmd = super().format_kernel_cmd(extra_arguments)
            # Replace the Python executable with our custom one
            if cmd:
                cmd[0] = self.custom_python_path
            return cmd
    
    return CustomKernelManager(custom_python_path=python_env)

def create_tslab_kernel(kernel_name):
    """Create a TSLAB kernel (tslab or jslab)"""
    return KernelManager(kernel_name=kernel_name)

def get_kernel_client(kernel_id):
    """Get kernel client by ID"""
    if kernel_id not in kernels:
        raise ValueError(f"Kernel {kernel_id} not found")
    return kernels[kernel_id]['client']

def shutdown_kernel(kernel_id):
    """Stop and remove a kernel"""
    if kernel_id not in kernels:
        raise ValueError(f"Kernel {kernel_id} not found")
    
    kernel_info = kernels[kernel_id]
    kernel_info['client'].stop_channels()
    kernel_info['manager'].shutdown_kernel()
    del kernels[kernel_id]
    
    print(f"Kernel {kernel_id} stopped and removed")

def execute_code_in_kernel(code: str, kernel_id: str, timeout: int = 30) -> Dict[str, Any]:
    """Execute code in Jupyter kernel and return structured result"""
    kc = get_kernel_client(kernel_id)
    
    result = {
        'success': True,
        'output': [],
        'result': None,
        'error': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        msg_id = kc.execute(code)
        
        while True:
            try:
                msg = kc.get_iopub_msg(timeout=timeout)
                
                if msg['msg_type'] == 'stream':
                    result['output'].append(msg['content']['text'])
                elif msg['msg_type'] == 'execute_result':
                    result['result'] = msg['content']['data']['text/plain']
                elif msg['msg_type'] == 'error':
                    result['success'] = False
                    result['error'] = {
                        'name': msg['content']['ename'],
                        'message': msg['content']['evalue'],
                        'traceback': msg['content']['traceback']
                    }
                elif msg['msg_type'] == 'status' and msg['content']['execution_state'] == 'idle':
                    break
            except Exception as e:
                if 'timeout' in str(e).lower():
                    result['success'] = False
                    result['error'] = {'name': 'Timeout', 'message': f'Timeout after {timeout}s'}
                break
                
    except Exception as e:
        result['success'] = False
        result['error'] = {'name': 'ExecutionError', 'message': str(e)}
    
    return result

# Create MCP server
mcp = FastMCP("Jupyter Kernel Server")

@mcp.tool(
    annotations={
        "title": "Start Jupyter Kernel",
        "description": "Create a new persistent Jupyter kernel for code execution in Python, TypeScript, or JavaScript",
        "destructiveHint": False,
        "readOnlyHint": False,
        "idempotentHint": False
    }
)
def start_kernel(
    env_path: Annotated[str, Field(
        title="Environment Path",
        description="Full path to language runtime executable (e.g., /usr/bin/python3, /usr/bin/node)",
        examples=["/usr/bin/python3", "/usr/bin/node", "python", "node"]
    )],
    language: Annotated[Optional[Literal["python", "typescript", "javascript"]], Field(
        title="Programming Language",
        description="Programming language for the kernel (python, typescript, or javascript). Defaults to python for backward compatibility.",
        default="python"
    )] = "python",
    kernel_id: Annotated[Optional[str], Field(
        title="Kernel ID", 
        description="Custom kernel identifier (auto-generated if not provided)",
        pattern="^[a-zA-Z0-9_-]+$"
    )] = None,
    python_env: Annotated[Optional[str], Field(
        title="Python Executable Path (deprecated)",
        description="DEPRECATED: Use env_path instead. Full path to Python executable for backward compatibility.",
        examples=["/usr/bin/python3", "/opt/conda/bin/python", "python"]
    )] = None
) -> KernelInfo:
    """
    Start a new Jupyter kernel with persistent state for code execution.
    """
    try:
        # Handle backward compatibility
        if python_env is not None:
            actual_env_path = python_env
            actual_language = "python"
        else:
            actual_env_path = env_path
            actual_language = language
        
        actual_id = create_kernel(actual_language, actual_env_path, kernel_id)
        return KernelInfo(
            kernel_id=actual_id,
            success=True,
            message=f'{actual_language.title()} kernel {actual_id} started successfully',
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return KernelInfo(
            kernel_id=kernel_id or "unknown",
            success=False,
            message="Failed to start kernel",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

@mcp.tool(
    annotations={
        "title": "Stop Kernel",
        "description": "Permanently stop and remove a Jupyter kernel",
        "destructiveHint": True,
        "readOnlyHint": False,
        "idempotentHint": True
    }
)
def stop_kernel(
    kernel_id: Annotated[str, Field(
        title="Kernel ID",
        description="ID of the kernel to stop (WARNING: This will permanently remove the kernel and all its state)",
        pattern="^[a-zA-Z0-9_-]+$"
    )]
) -> KernelInfo:
    """
    Stop and permanently remove a Jupyter kernel and all its state.
    """
    try:
        shutdown_kernel(kernel_id)
        return KernelInfo(
            kernel_id=kernel_id,
            success=True,
            message=f'Kernel {kernel_id} stopped successfully',
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return KernelInfo(
            kernel_id=kernel_id,
            success=False,
            message="Failed to stop kernel",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

@mcp.tool(
    annotations={
        "title": "List Active Kernels",
        "description": "Show all currently running Jupyter kernels",
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
def list_kernels() -> KernelList:
    """
    List all currently active Jupyter kernels with their status information.
    """
    kernel_info = {}
    for kid, kdata in kernels.items():
        kernel_info[kid] = {
            'created_at': kdata['created_at'].isoformat(),
            'status': 'running',
            'language': kdata['language'],
            'env_path': kdata['env_path']
        }
    
    return KernelList(
        success=True,
        kernels=kernel_info,
        count=len(kernels),
        timestamp=datetime.now().isoformat()
    )

@mcp.tool(
    annotations={
        "title": "Execute Python Code",
        "description": "Run Python code in a persistent kernel environment with maintained state",
        "destructiveHint": False,
        "readOnlyHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
def execute_code(
    code: Annotated[str, Field(
        title="Python Code",
        description="Python code to execute (variables persist between executions)",
        format="code",
        contentMediaType="text/x-python",
        examples=["print('Hello, World!')", "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3]})"]
    )],
    kernel_id: Annotated[str, Field(
        title="Kernel ID",
        description="ID of the kernel to execute code in (use list_kernels to see available kernels)",
        pattern="^[a-zA-Z0-9_-]+$"
    )],
    timeout: Annotated[int, Field(
        title="Timeout (seconds)",
        description="Maximum execution time in seconds",
        ge=1,
        le=300,
        default=30
    )] = 30
) -> ExecutionResult:
    """
    Execute Python code in a persistent Jupyter kernel with maintained state.
    """
    result = execute_code_in_kernel(code, kernel_id, timeout)
    return ExecutionResult(
        success=result['success'],
        output=result['output'],
        result=result['result'],
        error=result['error'],
        timestamp=result['timestamp']
    )

@mcp.tool(
    annotations={
        "title": "List Kernel Variables",
        "description": "Inspect all variables currently defined in a kernel's namespace",
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
def list_variables(
    kernel_id: Annotated[str, Field(
        title="Kernel ID",
        description="ID of the kernel to inspect variables from",
        pattern="^[a-zA-Z0-9_-]+$"
    )]
) -> VariableList:
    """
    List all variables currently defined in the specified kernel's namespace.
    """
    code = """
import sys
# Create a snapshot of globals to avoid "dictionary changed size during iteration"
globals_snapshot = dict(globals())
namespace_vars = {}
for name, value in globals_snapshot.items():
    if not name.startswith('_') and not callable(value) and name not in sys.modules:
        try:
            namespace_vars[name] = {
                'type': type(value).__name__,
                'repr': str(value)[:100] + ('...' if len(str(value)) > 100 else ''),
                'size': len(str(value))
            }
        except:
            # Skip variables that can't be stringified
            namespace_vars[name] = {
                'type': type(value).__name__,
                'repr': '<unable to display>',
                'size': 0
            }
namespace_vars
"""
    result = execute_code_in_kernel(code, kernel_id)
    
    if result['success'] and result['result']:
        try:
            vars_dict = eval(result['result'])
            variables = {
                name: VariableInfo(
                    name=name,
                    type=info['type'],
                    repr=info['repr'],
                    size=info['size']
                )
                for name, info in vars_dict.items()
            }
            return VariableList(
                success=True,
                variables=variables,
                count=len(variables),
                timestamp=datetime.now().isoformat(),
                kernel_id=kernel_id
            )
        except Exception as e:
            return VariableList(
                success=False,
                variables={},
                count=0,
                timestamp=datetime.now().isoformat(),
                kernel_id=kernel_id
            )
    else:
        return VariableList(
            success=False,
            variables={},
            count=0,
            timestamp=datetime.now().isoformat(),
            kernel_id=kernel_id
        )

@mcp.tool(
    annotations={
        "title": "Reset Kernel",
        "description": "Reset a kernel by clearing all variables and state",
        "destructiveHint": True,
        "readOnlyHint": False,
        "idempotentHint": True
    }
)
def reset_kernel(
    kernel_id: Annotated[str, Field(
        title="Kernel ID",
        description="ID of the kernel to reset (WARNING: This will clear all variables and state)",
        pattern="^[a-zA-Z0-9_-]+$"
    )]
) -> KernelInfo:
    """
    Reset a Jupyter kernel by clearing all variables and state while keeping the same ID.
    """
    try:
        # Get the original environment before stopping the kernel
        if kernel_id not in kernels:
            raise ValueError(f"Kernel {kernel_id} not found")
        
        original_language = kernels[kernel_id]['language']
        original_env_path = kernels[kernel_id]['env_path']
        
        # Stop the existing kernel
        shutdown_kernel(kernel_id)
        
        # Start a new kernel with the same ID and original environment
        create_kernel(original_language, original_env_path, kernel_id)
        
        return KernelInfo(
            kernel_id=kernel_id,
            success=True,
            message=f'Kernel {kernel_id} reset successfully',
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        return KernelInfo(
            kernel_id=kernel_id,
            success=False,
            message="Failed to reset kernel",
            timestamp=datetime.now().isoformat(),
            error=str(e)
        )

@mcp.tool(
    annotations={
        "title": "Get Kernel Status",
        "description": "Get detailed status information about a specific kernel",
        "readOnlyHint": True,
        "idempotentHint": True
    }
)
def get_kernel_status(
    kernel_id: Annotated[str, Field(
        title="Kernel ID",
        description="ID of the kernel to check status for",
        pattern="^[a-zA-Z0-9_-]+$"
    )]
) -> KernelStatus:
    """
    Get detailed status information about a specific Jupyter kernel.
    """
    if kernel_id not in kernels:
        return KernelStatus(
            kernel_id=kernel_id,
            status="not_found",
            created_at="",
            language="",
            env_path="",
            details={"error": f"Kernel {kernel_id} not found"}
        )
    
    kernel_data = kernels[kernel_id]
    
    # Get basic info based on kernel language
    language = kernel_data['language']
    if language == 'python':
        info_code = """
import sys, os
from datetime import datetime
try:
    import psutil
    memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
except ImportError:
    memory_mb = 0

{
    'runtime_version': sys.version,
    'pid': os.getpid(),
    'memory_usage_mb': memory_mb,
    'uptime': 'kernel_running',
    'current_time': datetime.now().isoformat()
}
"""
    else:  # TypeScript/JavaScript
        info_code = """
const os = require('os');
const process = require('process');

({
    runtime_version: process.version,
    pid: process.pid,
    memory_usage_mb: process.memoryUsage().rss / 1024 / 1024,
    uptime: 'kernel_running',
    current_time: new Date().toISOString()
})
"""
    
    try:
        result = execute_code_in_kernel(info_code, kernel_id)
        if result['success'] and result['result']:
            details = eval(result['result'])
        else:
            details = {'basic_info': 'unavailable'}
    except:
        details = {'status_check': 'failed'}
    
    return KernelStatus(
        kernel_id=kernel_id,
        status="running",
        created_at=kernel_data['created_at'].isoformat(),
        language=kernel_data['language'],
        env_path=kernel_data['env_path'],
        details=details
    )

@mcp.resource("kernel://variables/{kernel_id}")
def get_variables_resource(kernel_id: str) -> str:
    """
    Resource providing current kernel variables as text.
    """
    try:
        result = list_variables(kernel_id)
        if result['success'] and result['result']:
            vars_dict = eval(result['result'])
            output = f"Kernel {kernel_id} Variables:\n\n"
            for name, info in vars_dict.items():
                output += f"{name} ({info['type']}): {info['repr']}\n"
            return output
        else:
            return f"Error reading variables from kernel {kernel_id}"
    except Exception as e:
        return f"Kernel {kernel_id} not found or error: {str(e)}"

# Cleanup function
def cleanup():
    """Cleanup all kernels on exit"""
    for kernel_id in list(kernels.keys()):
        try:
            shutdown_kernel(kernel_id)
        except:
            pass

def main():
    """Main entry point for the MCP server"""
    import atexit
    print("Starting MCP Jupyter Kernel Server...")
    print("No kernels started by default - use start_kernel tool to create kernels")
    
    atexit.register(cleanup)
    print("Starting MCP protocol server...")
    mcp.run()

if __name__ == "__main__":
    main()