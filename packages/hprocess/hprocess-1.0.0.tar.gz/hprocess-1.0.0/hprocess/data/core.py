import os
import sys
import time
import inspect
import threading
import subprocess
import psutil
import json
import warnings
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from .moduledep import *

class ProcessError(Exception):
    """进程操作异常"""
    def __init__(self, message: str, pid: int = None):
        self.pid = pid
        self.message = message
        super().__init__(f"ProcessError (PID={pid}): {message}")

class ProcessInfo:
    """获取进程详细信息"""
    def __init__(self, identifier: str | int):
        """
        通过进程名或PID初始化
        :param identifier: 进程名(str)或PID(int)
        """
        self.identifier = identifier
        self.pid: Optional[int] = None
        self.name: Optional[str] = None
        self.command_line: Optional[str] = None
        self.image_path: Optional[str] = None
        self.status: Optional[str] = None
        self.parent_pid: Optional[int] = None
        self.cpu_percent: Optional[float] = None
        self.memory_usage: Optional[int] = None
        self.create_time: Optional[float] = None
        self.threads_count: Optional[int] = None
        self.user: Optional[str] = None
        self._process: Optional[psutil.Process] = None
        
        self._resolve_process()
        self._populate_info()
    
    def _resolve_process(self):
        """根据标识符解析进程"""
        if isinstance(self.identifier, int):
            # 如果是PID
            try:
                self._process = psutil.Process(self.identifier)
            except psutil.NoSuchProcess:
                raise ProcessError(f"找不到PID为 {self.identifier} 的进程")
        else:
            # 如果是进程名
            processes = []
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] == self.identifier:
                    processes.append(proc)
            
            if not processes:
                raise ProcessError(f"找不到名为 '{self.identifier}' 的进程")
            
            # 选择第一个找到的进程
            self._process = processes[0]
    
    def _populate_info(self):
        """填充进程信息"""
        if not self._process:
            return
            
        self.pid = self._process.pid
        self.name = self._process.name()
        
        try:
            self.command_line = " ".join(self._process.cmdline())
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            self.command_line = None
        
        try:
            self.image_path = self._process.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            self.image_path = None
        
        self.status = self._process.status()
        self.parent_pid = self._process.ppid()
        self.cpu_percent = self._process.cpu_percent(interval=0.1)
        self.memory_usage = self._process.memory_info().rss
        self.create_time = self._process.create_time()
        self.threads_count = self._process.num_threads()
        
        try:
            self.user = self._process.username()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            self.user = None
    
    def refresh(self):
        """刷新进程信息"""
        self._resolve_process()
        self._populate_info()
    
    def get_all_info(self) -> dict:
        """获取所有进程信息字典"""
        return {
            "pid": self.pid,
            "name": self.name,
            "command_line": self.command_line,
            "image_path": self.image_path,
            "status": self.status,
            "parent_pid": self.parent_pid,
            "cpu_percent": self.cpu_percent,
            "memory_usage": self.memory_usage,
            "create_time": self.create_time,
            "threads_count": self.threads_count,
            "user": self.user
        }
    
    def __str__(self):
        return (f"ProcessInfo(pid={self.pid}, name='{self.name}', "
                f"command_line='{self.command_line}', image_path='{self.image_path}', "
                f"status='{self.status}', parent_pid={self.parent_pid}, "
                f"cpu_percent={self.cpu_percent}%, memory_usage={self.memory_usage} bytes, "
                f"create_time={self.create_time}, threads={self.threads_count}, user='{self.user}')")

class ProcessWarning(Warning):
    """Base warning for process-related issues"""
    def __init__(self, message: str, feature: str = None):
        self.feature = feature
        self.message = message
        super().__init__(f"ProcessWarning: {message}")

class ProcessSystemWarning(ProcessWarning):
    """Warning for system-specific limitations"""
    def __init__(self, message: str, system: str, feature: str):
        self.system = system
        self.feature = feature
        message = f"{feature} may not work properly on {system}. {message}"
        super().__init__(message, feature)

class ProcessType(Enum):
    """Process type enumeration"""
    SYSTEM = 1
    USER = 2
    DAEMON = 3
    KERNEL = 4

class ProcessBase:
    """Base class for processes providing common functionality"""
    def __init__(self, name: str, pid: int = None):
        self.name = name
        self.pid = pid or os.getpid()
        self.creation_time = time.time()
        
    def get_info(self) -> Dict[str, Any]:
        """Get process information"""
        try:
            process = psutil.Process(self.pid)
            return {
                "name": self.name,
                "pid": self.pid,
                "status": process.status(),
                "cpu_percent": process.cpu_percent(),
                "memory_usage": process.memory_info().rss
            }
        except psutil.NoSuchProcess:
            raise ProcessError("Process not found", self.pid)

    def is_running(self) -> bool:
        """Check if the process is running"""
        return psutil.pid_exists(self.pid)

class ProcessEntity(ProcessBase):
    """Process entity representing an actual OS process"""
    def __init__(self, name: str, pid: int = None):
        super().__init__(name, pid)
        self.type = ProcessType.USER
        
    def set_type(self, process_type: ProcessType):
        """Set process type"""
        self.type = process_type
        
    def get_children(self) -> List[Dict[str, Any]]:
        """Get child process information"""
        try:
            process = psutil.Process(self.pid)
            return [{"pid": child.pid, "name": child.name()} 
                    for child in process.children()]
        except psutil.NoSuchProcess:
            raise ProcessError("Process not found", self.pid)

class ProcessInstance(ProcessBase):
    """Process instance managing the lifecycle of a specific process"""
    def __init__(self, name: str, target: Callable, args: tuple = ()):
        super().__init__(name)
        self.target = target
        self.args = args
        self.thread = threading.Thread(target=self._run)
        
    def _run(self):
        """Internal run method"""
        try:
            self.target(*self.args)
        except Exception as e:
            raise ProcessError(f"Process crashed: {str(e)}", self.pid)
            
    def start(self):
        """Start the process instance"""
        self.thread.start()
        self.pid = os.getpid()  # In real scenarios, multiprocessing might be used
        
    def join(self, timeout: float = None):
        """Wait for the process to finish"""
        self.thread.join(timeout)
        
    def terminate(self):
        """Terminate the process instance"""
        if self.thread.is_alive():
            # In actual implementation, process termination should be used here
            raise ProcessError("Termination not implemented in threading", self.pid)

class ProcessMethod:
    """Process method encapsulating executable operations"""
    def __init__(self, name: str, method: Callable):
        self.name = name
        self.method = method
        
    def execute(self, *args, **kwargs):
        """Execute the method and return the result"""
        return self.method(*args, **kwargs)
        
    def get_signature(self) -> str:
        """Get method signature"""
        return str(inspect.signature(self.method))

class ProcessFunction(ProcessMethod):
    """Specialized process function handling function operations"""
    def __init__(self, name: str, function: Callable):
        super().__init__(name, function)
        
    def benchmark(self, runs: int = 1000, *args, **kwargs) -> float:
        """Performance benchmarking"""
        start = time.perf_counter()
        for _ in range(runs):
            self.method(*args, **kwargs)
        return (time.perf_counter() - start) / runs

class ProcessClass:
    """Process class representing an instantiable process class"""
    def __init__(self, name: str, class_obj: type):
        self.name = name
        self.class_obj = class_obj
        self.methods = self._discover_methods()
        
    def _discover_methods(self) -> Dict[str, ProcessMethod]:
        """Discover public methods in the class"""
        return {
            name: ProcessMethod(name, method) 
            for name, method in inspect.getmembers(self.class_obj, inspect.isfunction)
            if not name.startswith('_')
        }
        
    def get_method(self, name: str) -> Optional[ProcessMethod]:
        """Get a specific method"""
        return self.methods.get(name)
    
    def create_instance(self, *args, **kwargs) -> object:
        """Create a class instance"""
        return self.class_obj(*args, **kwargs)

class ProcessModule:
    """Process module encapsulating a Python module"""
    def __init__(self, name: str, module):
        self.name = name
        self.module = module
        self.classes = self._discover_classes()
        self.functions = self._discover_functions()
        
    def _discover_classes(self) -> Dict[str, ProcessClass]:
        """Discover classes in the module"""
        return {
            name: ProcessClass(name, obj) 
            for name, obj in inspect.getmembers(self.module, inspect.isclass)
            if obj.__module__ == self.module.__name__
        }
        
    def _discover_functions(self) -> Dict[str, ProcessFunction]:
        """Discover functions in the module"""
        return {
            name: ProcessFunction(name, obj) 
            for name, obj in inspect.getmembers(self.module, inspect.isfunction)
            if obj.__module__ == self.module.__name__
        }
        
    def get_class(self, name: str) -> Optional[ProcessClass]:
        """Get a specific class"""
        return self.classes.get(name)
    
    def get_function(self, name: str) -> Optional[ProcessFunction]:
        """Get a specific function"""
        return self.functions.get(name)

class ProcessPackage:
    """Process package managing Python package structure"""
    def __init__(self, name: str):
        self.name = name
        self.modules: Dict[str, ProcessModule] = {}
        
    def add_module(self, module_name: str, module) -> ProcessModule:
        """Add a module to the package"""
        if module_name in self.modules:
            raise ValueError(f"Module {module_name} already exists")
        module_obj = ProcessModule(module_name, module)
        self.modules[module_name] = module_obj
        return module_obj
    
    def get_module(self, module_name: str) -> Optional[ProcessModule]:
        """Get a specific module"""
        return self.modules.get(module_name)

class ProcessLibrary(ProcessPackage):
    """Specialized process library handling third-party libraries"""
    def __init__(self, name: str, version: str):
        super().__init__(name)
        self.version = version
        
    def get_dependencies(self) -> List[str]:
        """Get library dependencies (simulated implementation)"""
        # Actual implementation should use importlib.metadata
        return ["dependency1", "dependency2"]
    
    def check_system_compatibility(self):
        """Check system compatibility for this library"""
        system = sys.platform
        if system == "darwin":
            warnings.warn(
                ProcessSystemWarning(
                    "Some features may not be available on macOS.", 
                    "macOS", 
                    self.name
                )
            )
        elif system in ["win32", "linux"]:
            warnings.warn(
                ProcessSystemWarning(
                    "Certain advanced features might have limited functionality.", 
                    system.capitalize(), 
                    self.name
                )
            )

class ProcessResource:
    """Process resource managing CPU/memory resources"""
    def __init__(self, pid: int):
        self.pid = pid
        try:
            self.process = psutil.Process(pid)
        except psutil.NoSuchProcess:
            raise ProcessError(f"Process with PID {pid} not found")
        
    def cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        return self.process.cpu_percent(interval=0.1)
    
    def memory_usage(self) -> int:
        """Get memory usage in bytes"""
        return self.process.memory_info().rss
    
    def io_counters(self) -> Dict[str, int]:
        """Get I/O statistics"""
        try:
            io = self.process.io_counters()
            return {
                "read_count": io.read_count,
                "write_count": io.write_count,
                "read_bytes": io.read_bytes,
                "write_bytes": io.write_bytes
            }
        except psutil.AccessDenied:
            warnings.warn(
                ProcessWarning("I/O counters not available due to access restrictions"),
                stacklevel=2
            )
            return {}
    
    def limit_cpu(self, percent: float):
        """Limit CPU usage (UNIX systems only)"""
        system = sys.platform
        
        if system == "darwin":
            raise ProcessSystemWarning(
                "This module is not available on macOS. CPU limiting requires Linux.", 
                "macOS", 
                "CPU Limiting"
            )
        
        if system not in ["linux", "win32"]:
            warnings.warn(
                ProcessSystemWarning(
                    "CPU limiting may not work as expected on this system.", 
                    system.capitalize(), 
                    "CPU Limiting"
                ),
                stacklevel=2
            )
        
        if system == "linux":
            # Linux implementation
            try:
                # This is a simplified implementation - actual should use cgroups
                self.process.cpu_affinity([0])
            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                raise ProcessError(f"Failed to limit CPU: {str(e)}", self.pid)
        elif system == "win32":
            # Windows implementation
            try:
                # Windows-specific CPU limiting approach
                self.process.nice(psutil.HIGH_PRIORITY_CLASS)
                warnings.warn(
                    ProcessSystemWarning(
                        "CPU limiting on Windows uses priority classes which is less precise than Linux cgroups.", 
                        "Windows", 
                        "CPU Limiting"
                    ),
                    stacklevel=2
                )
            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                raise ProcessError(f"Failed to limit CPU on Windows: {str(e)}", self.pid)
        else:
            raise NotImplementedError(f"CPU limiting not implemented for {system.capitalize()}")

class ProcessUtility:
    """Process utility class"""
    @staticmethod
    def find_process_by_name(name: str) -> List['ProcessEntity']:
        """Find processes by name"""
        processes = []
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == name:
                processes.append(ProcessEntity(name, proc.pid))
        return processes
    
    @staticmethod
    def get_system_load() -> Dict[str, float]:
        """Get system load average"""
        system = sys.platform
        if system == "win32":
            warnings.warn(
                ProcessSystemWarning(
                    "Load averages are not natively available on Windows. Values are simulated.", 
                    "Windows", 
                    "System Load"
                ),
                stacklevel=2
            )
            # Simulate load average for Windows
            cpu_percent = psutil.cpu_percent(interval=1) / 100
            return {
                "1min": cpu_percent * 1.2,
                "5min": cpu_percent * 0.9,
                "15min": cpu_percent * 0.8
            }
        else:
            load = os.getloadavg()
            return {
                "1min": load[0],
                "5min": load[1],
                "15min": load[2]
            }
    
    @staticmethod
    def get_system_warnings() -> List[ProcessSystemWarning]:
        """Get system compatibility warnings"""
        warnings_list = []
        system = sys.platform
        if system == "darwin":
            warnings_list.append(
                ProcessSystemWarning(
                    "Several advanced features are unavailable on macOS.", 
                    "macOS", 
                    "System Compatibility"
                )
            )
        elif system in ["win32", "linux"]:
            warnings_list.append(
                ProcessSystemWarning(
                    "Some features may have platform-specific limitations.", 
                    system.capitalize(), 
                    "System Compatibility"
                )
            )
        return warnings_list

class ProcessComponent:
    """Process component representing part of a process's functionality"""
    def __init__(self, name: str, process: ProcessEntity):
        self.name = name
        self.process = process
        self.status = "inactive"
        
    def activate(self):
        """Activate the component"""
        self.status = "active"
        
    def deactivate(self):
        """Deactivate the component"""
        self.status = "inactive"
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get component metrics (simulated)"""
        return {
            "status": self.status,
            "load": 0.75,
            "throughput": 100
        }

class ProcessAlias:
    """Process alias managing alternative names for processes"""
    def __init__(self, process: ProcessEntity):
        self.process = process
        self.aliases: Dict[str, str] = {}
        
    def add_alias(self, alias: str, description: str):
        """Add an alias"""
        self.aliases[alias] = description
        
    def resolve(self, alias: str) -> ProcessEntity:
        """Resolve a process by alias"""
        if alias in self.aliases:
            return self.process
        raise ValueError(f"Alias '{alias}' not found")

class ProcessCreate:
    """Process creator"""
    @staticmethod
    def from_command(command: str) -> ProcessEntity:
        """Create a process from a command"""
        try:
            process = subprocess.Popen(command, shell=True)
            return ProcessEntity(command, process.pid)
        except OSError as e:
            raise ProcessError(f"Command failed: {str(e)}")

    @staticmethod
    def from_function(func: Callable, args: tuple = ()) -> ProcessInstance:
        """Create a process instance from a function"""
        return ProcessInstance(func.__name__, func, args)

class ProcessKill:
    """Process terminator"""
    @staticmethod
    def terminate(process: ProcessEntity):
        """Terminate a process"""
        try:
            psutil.Process(process.pid).terminate()
        except psutil.NoSuchProcess:
            raise ProcessError("Process already terminated", process.pid)
            
    @staticmethod
    def force_kill(process: ProcessEntity):
        """Force kill a process"""
        try:
            psutil.Process(process.pid).kill()
        except psutil.NoSuchProcess:
            raise ProcessError("Process not found", process.pid)

class ProcessObject(ProcessBase):
    """Process object representing a generic process entity"""
    def __init__(self, name: str, obj: Any, pid: int = None):
        super().__init__(name, pid)
        self.obj = obj
        self.object_type = type(obj).__name__
        
    def serialize(self) -> Dict[str, Any]:
        """Serialize object information"""
        return {
            "name": self.name,
            "type": self.object_type,
            "size": sys.getsizeof(self.obj),
            "methods": dir(self.obj)
        }

class ProcessTool:
    """Process toolset providing utility functions"""
    def __init__(self):
        self.processes: List[ProcessEntity] = []
        
    def add_process(self, process: ProcessEntity):
        """Add a process to the toolset"""
        self.processes.append(process)
        
    def monitor(self, interval: float = 1.0, duration: float = 10.0):
        """Monitor process resource usage"""
        end_time = time.time() + duration
        while time.time() < end_time:
            for process in self.processes:
                try:
                    info = process.get_info()
                    print(f"[{process.name}] CPU: {info['cpu_percent']}% MEM: {info['memory_usage']/1e6:.2f}MB")
                except ProcessError:
                    print(f"[{process.name}] Process terminated")
            time.sleep(interval)
    
    def check_system_compatibility(self):
        """Check system compatibility for all processes"""
        system = sys.platform
        if system == "darwin":
            for process in self.processes:
                warnings.warn(
                    ProcessSystemWarning(
                        "This tool may have limited functionality on macOS.", 
                        "macOS", 
                        f"Process: {process.name}"
                    ),
                    stacklevel=2
                )
        elif system in ["win32", "linux"]:
            for process in self.processes:
                warnings.warn(
                    ProcessSystemWarning(
                        "Some features might not be fully supported on this platform.", 
                        system.capitalize(), 
                        f"Process: {process.name}"
                    ),
                    stacklevel=2
                )

import os
import sys
import time
import json
import signal
import threading
import subprocess
import psutil
import warnings
from enum import Enum
from typing import Dict, Any, List, Optional, Callable, Union

class ProcessError(Exception):
    """进程操作异常基类"""
    def __init__(self, message: str, pid: int = None):
        self.pid = pid
        self.message = message
        super().__init__(f"ProcessError (PID={pid}): {message}")

class ProcessState:
    """进程状态管理器"""
    def __init__(self, pid: int):
        self.pid = pid
        self._process = psutil.Process(pid)
        self.states: Dict[str, Dict] = {}
        
    def capture(self, state_name: str):
        """捕获当前进程状态"""
        try:
            state = {
                "timestamp": time.time(),
                "cpu_percent": self._process.cpu_percent(interval=0.1),
                "memory_usage": self._process.memory_info().rss,
                "num_threads": self._process.num_threads(),
                "num_handles": self._process.num_handles(),
                "status": self._process.status()
            }
            self.states[state_name] = state
            return state
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            raise ProcessError(f"State capture failed: {str(e)}", self.pid)
    
    def compare(self, state1: str, state2: str) -> Dict[str, Any]:
        """比较两个状态之间的差异"""
        if state1 not in self.states or state2 not in self.states:
            raise ProcessError("One or both states not found", self.pid)
            
        s1 = self.states[state1]
        s2 = self.states[state2]
        
        return {
            "cpu_delta": s2["cpu_percent"] - s1["cpu_percent"],
            "memory_delta": s2["memory_usage"] - s1["memory_usage"],
            "threads_delta": s2["num_threads"] - s1["num_threads"],
            "handles_delta": s2["num_handles"] - s1["num_handles"]
        }

class ProcessHook:
    """进程钩子管理器"""
    def __init__(self, process: 'ProcessEntity'):
        self.process = process
        self.hooks: Dict[str, Callable] = {}
        
    def register(self, event: str, callback: Callable):
        """注册事件钩子"""
        if event not in ["pre_start", "post_start", "pre_stop", "post_stop", "resource_alert"]:
            raise ProcessError(f"Unsupported hook event: {event}")
        self.hooks[event] = callback
        
    def trigger(self, event: str, *args):
        """触发事件钩子"""
        if event in self.hooks:
            try:
                return self.hooks[event](self.process, *args)
            except Exception as e:
                raise ProcessError(f"Hook execution failed: {str(e)}", self.process.pid)

class ProcessGuardian:
    """进程守护管理器"""
    def __init__(self, process: 'ProcessEntity'):
        self.process = process
        self.monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self.running = False
        self.thresholds = {
            "cpu": 90.0,
            "memory": 1024 * 1024 * 500  # 500MB
        }
        self.alerts = 0
        
    def set_thresholds(self, cpu: float, memory: int):
        """设置资源阈值"""
        self.thresholds["cpu"] = cpu
        self.thresholds["memory"] = memory
        
    def start(self):
        """启动守护监控"""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread.start()
        
    def _monitor(self):
        """监控进程资源使用"""
        while self.running:
            try:
                proc = psutil.Process(self.process.pid)
                cpu = proc.cpu_percent(interval=1)
                mem = proc.memory_info().rss
                
                if cpu > self.thresholds["cpu"]:
                    self.alerts += 1
                    warnings.warn(f"CPU overload detected: {cpu}% > {self.thresholds['cpu']}% (PID: {self.process.pid})")
                    
                if mem > self.thresholds["memory"]:
                    self.alerts += 1
                    warnings.warn(f"Memory overflow: {mem/(1024*1024):.2f}MB > {self.thresholds['memory']/(1024*1024):.2f}MB (PID: {self.process.pid})")
                    
                # 如果连续5次警报，尝试降低优先级
                if self.alerts >= 5:
                    self._adjust_priority(-1)
                    self.alerts = 0
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                self.running = False
                break
            time.sleep(5)
    
    def _adjust_priority(self, adjustment: int):
        """调整进程优先级"""
        try:
            current_nice = self.process.nice()
            new_nice = max(min(current_nice + adjustment, 19), -20)
            self.process.nice(new_nice)
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

class ProcessDependency:
    """进程依赖管理器"""
    def __init__(self, process: 'ProcessEntity'):
        self.process = process
        self.dependencies: Dict[str, str] = {}
        
    def add_dependency(self, dep_name: str, required_version: str = ""):
        """添加依赖项"""
        self.dependencies[dep_name] = required_version
            
    def verify(self) -> Dict[str, str]:
        """验证依赖是否满足"""
        results = {}
        for dep, req_version in self.dependencies.items():
            try:
                module = __import__(dep)
                version = getattr(module, '__version__', 'unknown')
                
                if req_version and version != req_version:
                    results[dep] = f"Version mismatch: installed={version}, required={req_version}"
                else:
                    results[dep] = f"OK (version {version})"
                    
            except ImportError:
                results[dep] = "Missing"
                
        return results

class ProcessRecovery:
    """进程恢复管理器"""
    def __init__(self, process: 'ProcessEntity'):
        self.process = process
        self.max_restarts = 3
        self.restart_count = 0
        self.last_restart = 0
        
    def restart(self, command: str) -> int:
        """重启进程并返回新PID"""
        if self.restart_count >= self.max_restarts:
            raise ProcessError("Max restart attempts exceeded", self.process.pid)
            
        if time.time() - self.last_restart < 5:
            raise ProcessError("Restart too frequent", self.process.pid)
            
        try:
            # 终止当前进程
            if psutil.pid_exists(self.process.pid):
                psutil.Process(self.process.pid).terminate()
                
            # 启动新进程
            new_proc = subprocess.Popen(command, shell=True)
            new_pid = new_proc.pid
            
            # 更新状态
            self.process.pid = new_pid
            self.restart_count += 1
            self.last_restart = time.time()
            
            return new_pid
        except (OSError, psutil.NoSuchProcess) as e:
            raise ProcessError(f"Restart failed: {str(e)}", self.process.pid)

class ProcessNetwork:
    """进程网络连接管理器"""
    def __init__(self, pid: int):
        self.pid = pid
        self._process = psutil.Process(pid)
        
    def get_connections(self) -> List[dict]:
        """获取所有网络连接"""
        try:
            conns = []
            for conn in self._process.connections():
                conn_dict = {
                    "family": conn.family.name,
                    "type": conn.type.name,
                    "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                    "status": conn.status
                }
                if conn.raddr:
                    conn_dict["remote"] = f"{conn.raddr.ip}:{conn.raddr.port}"
                conns.append(conn_dict)
            return conns
        except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
            raise ProcessError(f"Network info failed: {str(e)}", self.pid)
            
    def block_remote(self, ip: str):
        """阻止与指定远程IP的所有连接"""
        if sys.platform == "win32":
            # Windows 使用防火墙命令
            try:
                subprocess.run(
                    ["netsh", "advfirewall", "firewall", "add", "rule", 
                     f"name=Block_{ip}", "dir=out", "remoteip={ip}", "action=block"],
                    check=True
                )
                return True
            except subprocess.CalledProcessError as e:
                raise ProcessError(f"Firewall rule failed: {str(e)}", self.pid)
        else:
            # Linux 使用iptables
            try:
                subprocess.run(
                    ["iptables", "-A", "OUTPUT", "-p", "tcp", "-d", ip, "-j", "DROP"],
                    check=True
                )
                return True
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                raise ProcessError(f"iptables command failed: {str(e)}", self.pid)

class ProcessInjector:
    """进程代码注入器"""
    def __init__(self, pid: int):
        self.pid = pid
        
    def inject_shell(self, command: str) -> str:
        """向进程注入并执行shell命令"""
        try:
            # 使用gdb执行命令注入
            gdb_cmds = [
                "gdb",
                "--batch",
                "-p", str(self.pid),
                "-ex", f"call system(\"{command}\")",
                "-ex", "detach",
                "-ex", "quit"
            ]
            result = subprocess.run(
                gdb_cmds,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise ProcessError(f"Injection failed: {result.stderr}", self.pid)
                
            return result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise ProcessError(f"Injection execution failed: {str(e)}", self.pid)

class ProcessSignals:
    """进程信号处理器"""
    def __init__(self, pid: int):
        self.pid = pid
        self._process = psutil.Process(pid)
        
    def send(self, signal_name: str):
        """向进程发送信号"""
        try:
            # 将信号名转换为实际信号
            sig = getattr(signal, f"SIG{signal_name}", None)
            if not sig:
                raise ValueError(f"Invalid signal name: {signal_name}")
                
            self._process.send_signal(sig)
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError) as e:
            raise ProcessError(f"Signal failed: {str(e)}", self.pid)
            
    def handle(self, signal_name: str, handler: Callable):
        """设置信号处理函数"""
        try:
            sig = getattr(signal, f"SIG{signal_name}", None)
            if not sig:
                raise ValueError(f"Invalid signal name: {signal_name}")
                
            signal.signal(sig, handler)
            return True
        except ValueError as e:
            raise ProcessError(f"Signal handling failed: {str(e)}", self.pid)

class ProcessScheduler:
    """进程调度管理器"""
    def __init__(self, pid: int):
        self.pid = pid
        self._process = psutil.Process(pid)
        
    def set_priority(self, priority: int):
        """设置进程优先级"""
        try:
            # 确保优先级在有效范围内
            if sys.platform == "win32":
                if priority not in [psutil.IDLE_PRIORITY_CLASS, 
                                   psutil.BELOW_NORMAL_PRIORITY_CLASS,
                                   psutil.NORMAL_PRIORITY_CLASS,
                                   psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                                   psutil.HIGH_PRIORITY_CLASS,
                                   psutil.REALTIME_PRIORITY_CLASS]:
                    raise ValueError("Invalid priority class")
                self._process.nice(priority)
            else:
                if not (-20 <= priority <= 19):
                    raise ValueError("Priority must be between -20 and 19")
                self._process.nice(priority)
                
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError) as e:
            raise ProcessError(f"Priority set failed: {str(e)}", self.pid)

class ProcessDebugger:
    """进程调试器"""
    def __init__(self, pid: int):
        self.pid = pid
        
    def attach(self):
        """附加到进程进行调试"""
        try:
            # 使用gdb附加到进程
            gdb_process = subprocess.Popen(
                ["gdb", "-p", str(self.pid)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return gdb_process
        except FileNotFoundError:
            raise ProcessError("gdb not found", self.pid)
            
    def execute_command(self, gdb_process: subprocess.Popen, command: str) -> str:
        """在调试会话中执行命令"""
        try:
            gdb_process.stdin.write(f"{command}\n".encode())
            gdb_process.stdin.flush()
            
            output = b""
            while True:
                line = gdb_process.stdout.readline()
                if b"(gdb)" in line:
                    break
                output += line
                
            return output.decode().strip()
        except (BrokenPipeError, OSError) as e:
            raise ProcessError(f"Debug command failed: {str(e)}", self.pid)

class ProcessAnalyzer:
    """进程性能分析器"""
    def __init__(self, pid: int):
        self.pid = pid
        self._process = psutil.Process(pid)
        
    def profile(self, duration: float = 5.0) -> Dict[str, Any]:
        """分析进程性能"""
        cpu_percent = []
        memory_usage = []
        io_count = 0
        
        end_time = time.time() + duration
        while time.time() < end_time:
            try:
                cpu_percent.append(self._process.cpu_percent(interval=0.1))
                memory_usage.append(self._process.memory_info().rss)
                
                # 获取IO计数
                io = self._process.io_counters()
                io_count += io.read_count + io.write_count
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(0.1)
            
        return {
            "cpu_max": max(cpu_percent) if cpu_percent else 0,
            "cpu_avg": sum(cpu_percent)/len(cpu_percent) if cpu_percent else 0,
            "memory_max": max(memory_usage) if memory_usage else 0,
            "memory_avg": sum(memory_usage)/len(memory_usage) if memory_usage else 0,
            "io_operations": io_count
        }

class ProcessLock:
    """进程间文件锁"""
    def __init__(self, name: str):
        self.name = name
        self.lock_file = f"/tmp/{name}.lock"
        self.lock_handle = None
        
    def acquire(self, timeout: float = 30.0) -> bool:
        """获取锁"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # 使用独占创建模式
                fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self.lock_handle = fd
                # 写入当前PID
                os.write(fd, str(os.getpid()).encode())
                return True
            except FileExistsError:
                time.sleep(0.1)
        return False
        
    def release(self):
        """释放锁"""
        if self.lock_handle:
            os.close(self.lock_handle)
            os.unlink(self.lock_file)
            self.lock_handle = None
            return True
        return False

class ProcessQueue:
    """进程间通信队列"""
    def __init__(self, name: str, maxsize: int = 100):
        self.name = name
        self.queue_file = f"/tmp/{name}.queue"
        self.maxsize = maxsize
        self._lock = ProcessLock(f"{name}_queue_lock")
        
    def put(self, item: str):
        """放入队列"""
        if not self._lock.acquire():
            raise ProcessError("Failed to acquire lock for queue")
            
        try:
            # 检查队列大小
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r') as f:
                    count = sum(1 for _ in f)
                if count >= self.maxsize:
                    raise ProcessError("Queue is full")
            
            # 添加项目
            with open(self.queue_file, 'a') as f:
                f.write(item + "\n")
        finally:
            self._lock.release()
            
    def get(self) -> Optional[str]:
        """从队列获取"""
        if not self._lock.acquire():
            raise ProcessError("Failed to acquire lock for queue")
            
        try:
            if not os.path.exists(self.queue_file):
                return None
                
            with open(self.queue_file, 'r') as f:
                lines = f.readlines()
                
            if not lines:
                return None
                
            # 获取并移除第一项
            item = lines[0].strip()
            
            # 重写文件，移除第一行
            with open(self.queue_file, 'w') as f:
                f.writelines(lines[1:])
                
            return item
        finally:
            self._lock.release()

class ProcessConfig:
    """进程配置管理器"""
    def __init__(self, pid: int):
        self.pid = pid
        self.config_file = f"/tmp/process_{pid}.config"
        self.config = {}
        
    def load(self) -> bool:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                return True
            except (json.JSONDecodeError, OSError) as e:
                raise ProcessError(f"Config load failed: {str(e)}", self.pid)
        return False
        
    def save(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except OSError as e:
            raise ProcessError(f"Config save failed: {str(e)}", self.pid)
            
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
        
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)

class ProcessLogger:
    """进程日志管理器"""
    def __init__(self, pid: int):
        self.pid = pid
        self.log_file = f"/tmp/process_{pid}.log"
        
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [{self.pid}] {message}\n"
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except OSError as e:
            raise ProcessError(f"Log write failed: {str(e)}", self.pid)
            
    def tail(self, lines: int = 10) -> List[str]:
        """获取最后N行日志"""
        try:
            if not os.path.exists(self.log_file):
                return []
                
            with open(self.log_file, 'r') as f:
                return list(f.readlines()[-lines:])
        except OSError as e:
            raise ProcessError(f"Log read failed: {str(e)}", self.pid)