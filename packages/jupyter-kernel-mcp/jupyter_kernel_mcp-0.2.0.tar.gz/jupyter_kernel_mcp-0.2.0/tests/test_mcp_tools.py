#!/usr/bin/env python3
"""
Test suite for MCP tools integration
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jupyter_kernel_mcp.server import (
    start_kernel, stop_kernel, list_kernels, execute_code, 
    list_variables, reset_kernel, get_kernel_status, kernels
)


class TestMCPTools:
    """Test MCP tool functions"""
    
    def setup_method(self):
        """Clear kernels before each test"""
        # Clear any existing kernels
        kernel_ids = list(kernels.keys())
        for kid in kernel_ids:
            try:
                stop_kernel(kid)
            except:
                pass
        kernels.clear()
    
    def teardown_method(self):
        """Clean up after each test"""
        self.setup_method()
    
    def test_start_kernel_tool(self):
        """Test start_kernel MCP tool"""
        python_path = sys.executable
        
        result = start_kernel(env_path=python_path, kernel_id= "mcp-test")
        
        assert result.success is True
        assert result.kernel_id == "mcp-test"
        assert "started successfully" in result.message
        
        # Clean up
        stop_kernel("mcp-test")
    
    def test_start_kernel_invalid_python(self):
        """Test start_kernel with invalid Python path"""
        result = start_kernel(env_path="/invalid/python", kernel_id= "mcp-test")
        
        assert result.success is False
        assert "not found" in result.error
    
    def test_stop_kernel_tool(self):
        """Test stop_kernel MCP tool"""
        python_path = sys.executable
        start_kernel(env_path=python_path, kernel_id= "mcp-test")
        
        result = stop_kernel("mcp-test")
        
        assert result.success is True
        assert "stopped successfully" in result.message
    
    def test_stop_nonexistent_kernel(self):
        """Test stopping non-existent kernel"""
        result = stop_kernel("nonexistent")
        
        assert result.success is False
        assert "not found" in result.error
    
    def test_list_kernels_empty(self):
        """Test listing kernels when none exist"""
        result = list_kernels()
        
        assert result.success is True
        assert result.count == 0
        assert result.kernels == {}
    
    def test_list_kernels_with_kernels(self):
        """Test listing kernels when some exist"""
        python_path = sys.executable
        start_kernel(env_path=python_path, kernel_id= "kernel-1")
        start_kernel(env_path=python_path, kernel_id= "kernel-2")
        
        result = list_kernels()
        
        assert result.success is True
        assert result.count == 2
        assert "kernel-1" in result.kernels
        assert "kernel-2" in result.kernels
        
        # Clean up
        stop_kernel("kernel-1")
        stop_kernel("kernel-2")
    
    def test_execute_code_tool(self):
        """Test execute_code MCP tool"""
        python_path = sys.executable
        start_kernel(env_path=python_path, kernel_id= "mcp-test")
        
        result = execute_code("print('MCP Test')", "mcp-test")
        
        assert result.success is True
        assert 'MCP Test' in ''.join(result.output)
        
        # Clean up
        stop_kernel("mcp-test")
    
    def test_execute_code_nonexistent_kernel(self):
        """Test execute_code with non-existent kernel"""
        with pytest.raises(ValueError, match="not found"):
            execute_code("print('test')", "nonexistent")
    
    def test_list_variables_tool(self):
        """Test list_variables MCP tool"""
        python_path = sys.executable
        start_kernel(env_path=python_path, kernel_id= "mcp-test")
        
        # Set some variables
        execute_code("test_var = 42", "mcp-test")
        execute_code("test_list = [1, 2, 3]", "mcp-test")
        
        result = list_variables("mcp-test")
        
        assert result.success is True
        # Variables should be in the result
        assert 'test_var' in result.variables
        assert 'test_list' in result.variables
        
        # Clean up
        stop_kernel("mcp-test")
    
    def test_reset_kernel_tool(self):
        """Test reset_kernel MCP tool"""
        python_path = sys.executable
        start_kernel(env_path=python_path, kernel_id= "mcp-test")
        
        # Set a variable
        execute_code("persist_var = 'should be cleared'", "mcp-test")
        
        # Reset kernel
        result = reset_kernel("mcp-test")
        
        assert result.success is True
        assert "reset successfully" in result.message
        
        # Verify variable is gone
        exec_result = execute_code("print(persist_var)", "mcp-test")
        assert exec_result.success is False
        assert "NameError" in exec_result.error['name']
        
        # Clean up
        stop_kernel("mcp-test")
    
    def test_get_kernel_status_tool(self):
        """Test get_kernel_status MCP tool"""
        python_path = sys.executable
        start_kernel(env_path=python_path, kernel_id= "mcp-test")
        
        result = get_kernel_status("mcp-test")
        
        # Should return some status info (even if basic)
        assert result.status == "running"
        assert result.kernel_id == "mcp-test"
        
        # Clean up
        stop_kernel("mcp-test")


class TestMCPToolsIntegration:
    """Test MCP tools working together"""
    
    def setup_method(self):
        """Clear kernels before each test"""
        kernel_ids = list(kernels.keys())
        for kid in kernel_ids:
            try:
                stop_kernel(kid)
            except:
                pass
        kernels.clear()
    
    def teardown_method(self):
        """Clean up after each test"""
        self.setup_method()
    
    def test_full_workflow(self):
        """Test a complete MCP workflow"""
        python_path = sys.executable
        
        # 1. Start kernel
        start_result = start_kernel(env_path=python_path, kernel_id= "workflow-test")
        assert start_result.success is True
        
        # 2. Execute some code
        exec_result = execute_code("""
import random
data = [random.randint(1, 100) for _ in range(10)]
total = sum(data)
print(f"Generated {len(data)} numbers, total: {total}")
total
""", "workflow-test")
        assert exec_result.success is True
        assert 'Generated 10 numbers' in ''.join(exec_result.output)
        
        # 3. List variables
        vars_result = list_variables("workflow-test")
        assert vars_result.success is True
        assert 'data' in vars_result.variables
        assert 'total' in vars_result.variables
        
        # 4. Continue computation using existing variables
        continue_result = execute_code("average = total / len(data); print(f'Average: {average}')", "workflow-test")
        assert continue_result.success is True
        assert 'Average:' in ''.join(continue_result.output)
        
        # 5. List kernels
        list_result = list_kernels()
        assert list_result.success is True
        assert list_result.count == 1
        assert "workflow-test" in list_result.kernels
        
        # 6. Clean up
        stop_result = stop_kernel("workflow-test")
        assert stop_result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])