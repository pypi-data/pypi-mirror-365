from .core import *

def getProcessInfo(identifier: str | int) -> dict:
    """获取进程详细信息字典"""
    return ProcessInfo(identifier).get_all_info()

def getProcessSummary(identifier: str | int) -> str:
    """获取进程信息摘要"""
    info = ProcessInfo(identifier)
    return f"{info.name} (PID:{info.pid}) CPU:{info.cpu_percent}% MEM:{info.memory_usage/1e6:.2f}MB"

def listAllProcesses() -> List[ProcessEntity]:
    """获取所有运行中的进程列表"""
    return [ProcessEntity(proc.info['name'], proc.pid) for proc in psutil.process_iter(['name'])]

# 进程控制函数
def startProcess(command: str) -> ProcessEntity:
    """通过命令行启动新进程"""
    return ProcessCreate.from_command(command)

def terminateProcess(process: ProcessEntity):
    """安全终止进程"""
    ProcessKill.terminate(process)

def killProcess(process: ProcessEntity):
    """强制结束进程"""
    ProcessKill.force_kill(process)

# 进程监控函数
def monitorProcess(pid: int, interval: float = 1.0, duration: float = 10.0):
    """监控指定进程的资源使用情况"""
    tool = ProcessTool()
    tool.add_process(ProcessEntity("", pid))
    tool.monitor(interval, duration)

def trackCpuUsage(pid: int, samples: int = 5) -> List[float]:
    """跟踪进程的CPU使用率"""
    resource = ProcessResource(pid)
    return [resource.cpu_usage() for _ in range(samples)]

# 系统级函数
def getSystemLoad() -> dict:
    """获取系统负载信息"""
    return ProcessUtility.get_system_load()

def checkPlatformCompatibility():
    """检查当前系统兼容性"""
    for warning in ProcessUtility.get_system_warnings():
        print(f"WARNING: {warning}")

# 资源管理函数
def limitProcessCpu(pid: int, percent: float):
    """限制进程的CPU使用率"""
    ProcessResource(pid).limit_cpu(percent)

def getProcessMemoryUsage(pid: int) -> float:
    """获取进程内存使用(MB)"""
    return ProcessResource(pid).memory_usage() / (1024 * 1024)

# 别名管理函数
def createProcessAlias(process: ProcessEntity, alias: str, description: str):
    """为进程创建别名"""
    ProcessAlias(process).add_alias(alias, description)

# 进程分析函数
def findProcessesByName(name: str) -> List[ProcessEntity]:
    """按名称查找进程"""
    return ProcessUtility.find_process_by_name(name)

def getProcessChildren(pid: int) -> List[dict]:
    """获取子进程信息"""
    return ProcessEntity("", pid).get_children()

# 进程工具函数
def benchmarkFunction(func: Callable, runs: int = 1000, *args, **kwargs) -> float:
    """函数性能基准测试(毫秒)"""
    return ProcessFunction(func.__name__, func).benchmark(runs, *args, **kwargs) * 1000

def getClassMethods(class_obj: type) -> Dict[str, str]:
    """获取类的公共方法签名"""
    return {name: method.get_signature() 
            for name, method in ProcessClass(class_obj.__name__, class_obj).methods.items()}

# 进程状态管理
def refreshProcessInfo(identifier: str | int):
    """刷新进程信息"""
    ProcessInfo(identifier).refresh()

def isProcessRunning(pid: int) -> bool:
    """检查进程是否在运行"""
    return ProcessBase("", pid).is_running()

# 高级功能函数
def createComponent(process: ProcessEntity, name: str) -> ProcessComponent:
    """为进程创建组件"""
    return ProcessComponent(name, process)

def activateProcessComponent(component: ProcessComponent):
    """激活进程组件"""
    component.activate()

# 第三方库管理
def checkLibraryCompatibility(lib_name: str, version: str):
    """检查第三方库兼容性"""
    library = ProcessLibrary(lib_name, version)
    library.check_system_compatibility()
    print(f"Checked {lib_name} v{version} compatibility")

# 进程对象分析
def analyzeProcessObject(obj: Any, name: str = None) -> dict:
    """分析进程相关对象"""
    return ProcessObject(name or type(obj).__name__, obj).serialize()

# 进程状态管理函数
def captureProcessState(pid: int, state_name: str) -> dict:
    """捕获进程状态"""
    return ProcessState(pid).capture(state_name)

def compareProcessStates(pid: int, state1: str, state2: str) -> dict:
    """比较两个进程状态"""
    return ProcessState(pid).compare(state1, state2)

# 进程钩子管理函数
def registerProcessHook(process: ProcessEntity, event: str, callback: Callable):
    """注册进程事件钩子"""
    ProcessHook(process).register(event, callback)

def triggerProcessHook(process: ProcessEntity, event: str, *args):
    """触发进程事件钩子"""
    ProcessHook(process).trigger(event, *args)

# 进程守护函数
def startProcessGuardian(process: ProcessEntity, cpu_threshold: float, mem_threshold_mb: float):
    """启动进程守护监控"""
    guardian = ProcessGuardian(process)
    guardian.set_thresholds(cpu_threshold, int(mem_threshold_mb * 1024 * 1024))
    guardian.start()
    return guardian

# 依赖管理函数
def addProcessDependency(process: ProcessEntity, dep_name: str, version: str = ""):
    """添加进程依赖"""
    ProcessDependency(process).add_dependency(dep_name, version)

def verifyProcessDependencies(process: ProcessEntity) -> dict:
    """验证进程依赖"""
    return ProcessDependency(process).verify()

# 进程恢复函数
def restartProcess(process: ProcessEntity, command: str) -> int:
    """重启进程并返回新PID"""
    return ProcessRecovery(process).restart(command)

# 网络管理函数
def getProcessConnections(pid: int) -> list:
    """获取进程网络连接"""
    return ProcessNetwork(pid).get_connections()

def blockRemoteIp(pid: int, ip: str):
    """阻止进程连接指定IP"""
    ProcessNetwork(pid).block_remote(ip)

# 进程注入函数
def injectProcessCommand(pid: int, command: str) -> str:
    """向进程注入并执行命令"""
    return ProcessInjector(pid).inject_shell(command)

# 信号处理函数
def sendProcessSignal(pid: int, signal_name: str):
    """向进程发送信号"""
    ProcessSignals(pid).send(signal_name)

def handleProcessSignal(signal_name: str, handler: Callable):
    """设置信号处理函数"""
    ProcessSignals(os.getpid()).handle(signal_name, handler)

# 调度管理函数
def setProcessPriority(pid: int, priority: int):
    """设置进程优先级"""
    ProcessScheduler(pid).set_priority(priority)

# 调试函数
def attachToProcess(pid: int) -> subprocess.Popen:
    """附加调试器到进程"""
    return ProcessDebugger(pid).attach()

def debugProcessCommand(gdb_process: subprocess.Popen, command: str) -> str:
    """在调试会话中执行命令"""
    return ProcessDebugger(gdb_process.pid).execute_command(gdb_process, command)

# 性能分析函数
def profileProcess(pid: int, duration: float = 5.0) -> dict:
    """分析进程性能"""
    return ProcessAnalyzer(pid).profile(duration)

# 进程锁函数
def acquireProcessLock(name: str, timeout: float = 30.0) -> bool:
    """获取进程锁"""
    return ProcessLock(name).acquire(timeout)

def releaseProcessLock(name: str):
    """释放进程锁"""
    return ProcessLock(name).release()

# 进程队列函数
def putProcessQueue(name: str, item: str):
    """向进程队列放入数据"""
    ProcessQueue(name).put(item)

def getProcessQueue(name: str) -> str:
    """从进程队列获取数据"""
    return ProcessQueue(name).get()

# 配置管理函数
def loadProcessConfig(pid: int) -> bool:
    """加载进程配置"""
    return ProcessConfig(pid).load()

def saveProcessConfig(pid: int) -> bool:
    """保存进程配置"""
    return ProcessConfig(pid).save()

def setProcessConfig(pid: int, key: str, value: Any):
    """设置进程配置项"""
    ProcessConfig(pid).set(key, value)

def getProcessConfig(pid: int, key: str, default: Any = None) -> Any:
    """获取进程配置项"""
    return ProcessConfig(pid).get(key, default)

# 日志管理函数
def logProcessMessage(pid: int, message: str, level: str = "INFO"):
    """记录进程日志"""
    ProcessLogger(pid).log(message, level)

def tailProcessLog(pid: int, lines: int = 10) -> list:
    """获取进程日志尾部"""
    return ProcessLogger(pid).tail(lines)

# 进程工具函数
def monitorProcessResource(pid: int, interval: float = 1.0, duration: float = 10.0):
    """监控进程资源使用情况"""
    end_time = time.time() + duration
    analyzer = ProcessAnalyzer(pid)
    
    while time.time() < end_time:
        try:
            info = analyzer.profile(interval)
            print(f"[PID:{pid}] CPU: {info['cpu_avg']:.1f}% MEM: {info['memory_avg']/1e6:.2f}MB IO: {info['io_operations']}")
        except ProcessError:
            print(f"[PID:{pid}] Process terminated")
            break
        time.sleep(interval)

def analyzeProcessDependencies(pid: int) -> dict:
    """分析进程依赖关系"""
    process = ProcessEntity("", pid)
    return ProcessDependency(process).verify()

def createProcessAlias(pid: int, alias: str):
    """为进程创建别名配置"""
    config = ProcessConfig(pid)
    config.load()
    config.set("alias", alias)
    config.save()
    return alias

def getProcessAlias(pid: int) -> str:
    """获取进程别名"""
    config = ProcessConfig(pid)
    config.load()
    return config.get("alias", f"Process_{pid}")