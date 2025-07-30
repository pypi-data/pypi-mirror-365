"""
Subprocess management plugin for YAPP framework.
Provides safe subprocess execution with process monitoring, timeout handling,
and resource management through the YAPP exposer system.
"""

import asyncio
import os
import signal
import subprocess
import threading
import time
import uuid
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from ...result import Result, Ok, Err
from ...exposers.base import BaseExposer


class ProcessState(Enum):
    """Process execution states."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


@dataclass
class ProcessConfig:
    """Configuration for subprocess execution."""
    command: Union[str, List[str]]
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: Optional[float] = None
    shell: bool = False
    capture_output: bool = True
    text: bool = True
    input_data: Optional[str] = None
    
    # Resource limits
    max_memory_mb: Optional[int] = None
    max_cpu_percent: Optional[float] = None
    
    # Callbacks
    stdout_callback: Optional[Callable[[str], None]] = None
    stderr_callback: Optional[Callable[[str], None]] = None
    completion_callback: Optional[Callable[['ProcessResult'], None]] = None


@dataclass
class ProcessResult:
    """Result of subprocess execution."""
    process_id: str
    command: Union[str, List[str]]
    returncode: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    state: ProcessState = ProcessState.PENDING
    error_message: Optional[str] = None
    pid: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None


class ProcessMonitor:
    """Monitors running processes for resource usage and health."""
    
    def __init__(self):
        self._monitoring = {}
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()
    
    def start_monitoring(self, process_id: str, process: subprocess.Popen, 
                        config: ProcessConfig) -> None:
        """Start monitoring a process."""
        self._monitoring[process_id] = {
            'process': process,
            'config': config,
            'start_time': time.time(),
            'max_memory': 0.0,
            'max_cpu': 0.0
        }
        
        if not self._monitor_thread:
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
    
    def stop_monitoring(self, process_id: str) -> Dict[str, Any]:
        """Stop monitoring a process and return stats."""
        if process_id in self._monitoring:
            stats = self._monitoring.pop(process_id)
            return {
                'max_memory_mb': stats['max_memory'],
                'max_cpu_percent': stats['max_cpu'],
                'execution_time': time.time() - stats['start_time']
            }
        return {}
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        try:
            import psutil
            has_psutil = True
        except ImportError:
            has_psutil = False
        
        while not self._stop_monitoring.is_set():
            if not has_psutil:
                time.sleep(1)
                continue
            
            for process_id, monitor_data in list(self._monitoring.items()):
                try:
                    process = monitor_data['process']
                    config = monitor_data['config']
                    
                    if process.poll() is not None:
                        # Process finished
                        continue
                    
                    # Get process info
                    try:
                        proc = psutil.Process(process.pid)
                        memory_mb = proc.memory_info().rss / 1024 / 1024
                        cpu_percent = proc.cpu_percent()
                        
                        # Update maximums
                        monitor_data['max_memory'] = max(monitor_data['max_memory'], memory_mb)
                        monitor_data['max_cpu'] = max(monitor_data['max_cpu'], cpu_percent)
                        
                        # Check limits
                        if config.max_memory_mb and memory_mb > config.max_memory_mb:
                            process.terminate()
                            continue
                        
                        if config.max_cpu_percent and cpu_percent > config.max_cpu_percent:
                            process.terminate()
                            continue
                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                except Exception:
                    pass
            
            time.sleep(0.5)
    
    def shutdown(self):
        """Shutdown the monitor."""
        self._stop_monitoring.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)


class SubprocessManager:
    """
    Main subprocess manager providing safe process execution.
    Integrates with YAPP framework through exposer system.
    """
    
    def __init__(self):
        self._processes: Dict[str, ProcessResult] = {}
        self._active_processes: Dict[str, subprocess.Popen] = {}
        self._monitor = ProcessMonitor()
        self._lock = threading.RLock()
    
    def execute_call(self, **kwargs) -> Any:
        """
        YAPP custom object interface for executing subprocess calls.
        
        Args:
            **kwargs: Command configuration (command, timeout, etc.)
            
        Returns:
            ProcessResult or error message
        """
        try:
            config = ProcessConfig(**kwargs)
            result = self.execute(config)
            
            if result.is_ok():
                return result.unwrap()
            else:
                return {"error": result.as_error()}
        except Exception as e:
            return {"error": str(e)}
    
    async def execute_call_async(self, **kwargs) -> Any:
        """
        YAPP custom object interface for async subprocess calls.
        
        Args:
            **kwargs: Command configuration (command, timeout, etc.)
            
        Returns:
            ProcessResult or error message
        """
        try:
            config = ProcessConfig(**kwargs)
            result = await self.execute_async(config)
            
            if result.is_ok():
                return result.unwrap()
            else:
                return {"error": result.as_error()}
        except Exception as e:
            return {"error": str(e)}
    
    def execute(self, config: ProcessConfig) -> Result[ProcessResult]:
        """
        Execute a subprocess with the given configuration.
        
        Args:
            config: Process configuration
            
        Returns:
            Result containing ProcessResult
        """
        process_id = str(uuid.uuid4()).replace('-', '')
        
        result = ProcessResult(
            process_id=process_id,
            command=config.command,
            state=ProcessState.PENDING
        )
        
        with self._lock:
            self._processes[process_id] = result
        
        try:
            start_time = time.time()
            
            # Prepare command
            if isinstance(config.command, str):
                cmd = config.command if config.shell else config.command.split()
            else:
                cmd = config.command
            
            # Prepare environment
            env = os.environ.copy()
            if config.env:
                env.update(config.env)
            
            # Start process
            process = subprocess.Popen(
                cmd,
                cwd=config.cwd,
                env=env,
                shell=config.shell,
                stdout=subprocess.PIPE if config.capture_output else None,
                stderr=subprocess.PIPE if config.capture_output else None,
                stdin=subprocess.PIPE if config.input_data else None,
                text=config.text
            )
            
            result.pid = process.pid
            result.state = ProcessState.RUNNING
            
            with self._lock:
                self._active_processes[process_id] = process
            
            # Start monitoring
            self._monitor.start_monitoring(process_id, process, config)
            
            # Execute with timeout
            try:
                stdout, stderr = process.communicate(
                    input=config.input_data,
                    timeout=config.timeout
                )
                
                result.returncode = process.returncode
                result.stdout = stdout or ""
                result.stderr = stderr or ""
                result.execution_time = time.time() - start_time
                
                if process.returncode == 0:
                    result.state = ProcessState.COMPLETED
                else:
                    result.state = ProcessState.FAILED
                    result.error_message = f"Process exited with code {process.returncode}"
            
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                
                result.state = ProcessState.TIMEOUT
                result.error_message = f"Process timed out after {config.timeout} seconds"
                result.execution_time = time.time() - start_time
            
            # Get monitoring stats
            monitor_stats = self._monitor.stop_monitoring(process_id)
            result.memory_usage_mb = monitor_stats.get('max_memory_mb')
            result.cpu_usage_percent = monitor_stats.get('max_cpu_percent')
            
            # Call completion callback
            if config.completion_callback:
                try:
                    config.completion_callback(result)
                except Exception:
                    pass
            
            with self._lock:
                self._active_processes.pop(process_id, None)
                self._processes[process_id] = result
            
            # Always return Ok(result) - the Result indicates successful execution attempt
            # The ProcessResult.state indicates whether the process itself succeeded
            return Ok(result)
        
        except Exception as e:
            result.state = ProcessState.FAILED
            result.error_message = str(e)
            result.execution_time = time.time() - start_time if 'start_time' in locals() else 0.0
            
            with self._lock:
                self._active_processes.pop(process_id, None)
                self._processes[process_id] = result
            
            return Err(str(e))
    
    async def execute_async(self, config: ProcessConfig) -> Result[ProcessResult]:
        """
        Execute subprocess asynchronously.
        
        Args:
            config: Process configuration
            
        Returns:
            Result containing ProcessResult
        """
        process_id = str(uuid.uuid4()).replace('-', '')
        
        result = ProcessResult(
            process_id=process_id,
            command=config.command,
            state=ProcessState.PENDING
        )
        
        with self._lock:
            self._processes[process_id] = result
        
        try:
            start_time = time.time()
            
            # Prepare command
            if isinstance(config.command, str):
                cmd = config.command if config.shell else config.command.split()
            else:
                cmd = config.command
            
            # Prepare environment
            env = os.environ.copy()
            if config.env:
                env.update(config.env)
            
            # Start async process
            process = await asyncio.create_subprocess_exec(
                *cmd if not config.shell else ['/bin/sh', '-c', config.command],
                cwd=config.cwd,
                env=env,
                stdout=asyncio.subprocess.PIPE if config.capture_output else None,
                stderr=asyncio.subprocess.PIPE if config.capture_output else None,
                stdin=asyncio.subprocess.PIPE if config.input_data else None
            )
            
            result.pid = process.pid
            result.state = ProcessState.RUNNING
            
            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(
                        input=config.input_data.encode() if config.input_data else None
                    ),
                    timeout=config.timeout
                )
                
                result.returncode = process.returncode
                result.stdout = stdout.decode() if stdout else ""
                result.stderr = stderr.decode() if stderr else ""
                result.execution_time = time.time() - start_time
                
                if process.returncode == 0:
                    result.state = ProcessState.COMPLETED
                else:
                    result.state = ProcessState.FAILED
                    result.error_message = f"Process exited with code {process.returncode}"
            
            except asyncio.TimeoutError:
                process.terminate()
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                
                result.state = ProcessState.TIMEOUT
                result.error_message = f"Process timed out after {config.timeout} seconds"
                result.execution_time = time.time() - start_time
            
            # Call completion callback
            if config.completion_callback:
                try:
                    config.completion_callback(result)
                except Exception:
                    pass
            
            with self._lock:
                self._processes[process_id] = result
            
            # Always return Ok(result) - the Result indicates successful execution attempt
            # The ProcessResult.state indicates whether the process itself succeeded
            return Ok(result)
        
        except Exception as e:
            result.state = ProcessState.FAILED
            result.error_message = str(e)
            result.execution_time = time.time() - start_time if 'start_time' in locals() else 0.0
            
            with self._lock:
                self._processes[process_id] = result
            
            return Err(str(e))
    
    def get_process_result(self, process_id: str) -> Optional[ProcessResult]:
        """Get result for a specific process."""
        with self._lock:
            return self._processes.get(process_id)
    
    def list_processes(self) -> List[ProcessResult]:
        """List all process results."""
        with self._lock:
            return list(self._processes.values())
    
    def cancel_process(self, process_id: str) -> bool:
        """Cancel a running process."""
        with self._lock:
            if process_id in self._active_processes:
                process = self._active_processes[process_id]
                try:
                    process.terminate()
                    
                    # Update result
                    if process_id in self._processes:
                        result = self._processes[process_id]
                        result.state = ProcessState.CANCELLED
                        result.error_message = "Process cancelled by user"
                    
                    return True
                except Exception:
                    return False
            return False
    
    def cleanup_completed(self, max_age_hours: float = 24.0) -> int:
        """Clean up old completed processes."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        removed_count = 0
        
        with self._lock:
            to_remove = []
            for process_id, result in self._processes.items():
                if (result.state in [ProcessState.COMPLETED, ProcessState.FAILED, 
                                   ProcessState.TIMEOUT, ProcessState.CANCELLED] and
                    time.time() - result.execution_time > cutoff_time):
                    to_remove.append(process_id)
            
            for process_id in to_remove:
                del self._processes[process_id]
                removed_count += 1
        
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get subprocess manager statistics."""
        with self._lock:
            states = {}
            for result in self._processes.values():
                state = result.state.value
                states[state] = states.get(state, 0) + 1
            
            return {
                'total_processes': len(self._processes),
                'active_processes': len(self._active_processes),
                'states': states,
                'memory_usage': sum(r.memory_usage_mb or 0 for r in self._processes.values()),
                'avg_execution_time': sum(r.execution_time for r in self._processes.values()) / 
                                    max(len(self._processes), 1)
            }
    
    def shutdown(self):
        """Shutdown the subprocess manager."""
        # Cancel all active processes
        with self._lock:
            for process_id in list(self._active_processes.keys()):
                self.cancel_process(process_id)
        
        # Shutdown monitor
        self._monitor.shutdown()


class SubprocessExposer(BaseExposer):
    """
    YAPP exposer for subprocess management.
    Integrates SubprocessManager with the YAPP framework.
    """
    
    def __init__(self):
        super().__init__()
        self.manager = SubprocessManager()
    
    def expose(self, obj, name: str) -> Result[None]:
        """Expose subprocess manager functionality."""
        if isinstance(obj, SubprocessManager):
            self.manager = obj
            return Ok(None)
        elif callable(obj):
            # Wrap function to execute as subprocess
            return self._expose_function_as_subprocess(obj, name)
        else:
            return Err(f"Cannot expose {type(obj)} as subprocess")
    
    def _expose_function_as_subprocess(self, func: Callable, name: str) -> Result[None]:
        """Expose a function to run as subprocess."""
        # This would need more implementation for function serialization
        return Ok(None)
    
    def run(self, obj, *args, **kwargs) -> Result[Any]:
        """Execute subprocess through manager."""
        if isinstance(obj, ProcessConfig):
            return self.manager.execute(obj)
        elif isinstance(obj, dict):
            # Convert dict to ProcessConfig
            try:
                config = ProcessConfig(**obj)
                return self.manager.execute(config)
            except Exception as e:
                return Err(f"Invalid process configuration: {e}")
        else:
            return Err("Expected ProcessConfig or dict")
    
    async def run_async(self, obj, *args, **kwargs) -> Result[Any]:
        """Execute subprocess asynchronously through manager."""
        if isinstance(obj, ProcessConfig):
            return await self.manager.execute_async(obj)
        elif isinstance(obj, dict):
            # Convert dict to ProcessConfig
            try:
                config = ProcessConfig(**obj)
                return await self.manager.execute_async(config)
            except Exception as e:
                return Err(f"Invalid process configuration: {e}")
        else:
            return Err("Expected ProcessConfig or dict")


# Convenience functions for easy integration
def create_subprocess_manager() -> SubprocessManager:
    """Create a new subprocess manager instance."""
    return SubprocessManager()


def create_process_config(command: Union[str, List[str]], 
                         timeout: Optional[float] = None,
                         cwd: Optional[str] = None,
                         **kwargs) -> ProcessConfig:
    """Create a process configuration."""
    return ProcessConfig(command=command, timeout=timeout, cwd=cwd, **kwargs)


def execute_command(command: Union[str, List[str]], 
                   timeout: Optional[float] = None,
                   **kwargs) -> Result[ProcessResult]:
    """Quick command execution."""
    manager = SubprocessManager()
    config = ProcessConfig(command=command, timeout=timeout, **kwargs)
    return manager.execute(config)


async def execute_command_async(command: Union[str, List[str]], 
                               timeout: Optional[float] = None,
                               **kwargs) -> Result[ProcessResult]:
    """Quick async command execution."""
    manager = SubprocessManager()
    config = ProcessConfig(command=command, timeout=timeout, **kwargs)
    return await manager.execute_async(config)