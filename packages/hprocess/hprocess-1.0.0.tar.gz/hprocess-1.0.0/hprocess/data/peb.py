import ctypes
from ctypes import wintypes
import sys

class PEBWarning(UserWarning):
    """PEB相关警告"""
    pass  

# 定义基本结构
class UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", wintypes.LPWSTR)
    ]

class LIST_ENTRY(ctypes.Structure):
    pass

LIST_ENTRY._fields_ = [
    ("Flink", ctypes.POINTER(LIST_ENTRY)),
    ("Blink", ctypes.POINTER(LIST_ENTRY))
]

class LARGE_INTEGER(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG)
    ]

class ULARGE_INTEGER(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.DWORD)
    ]

# 32位PEB结构
class PEB32(ctypes.Structure):
    _fields_ = [
        ("InheritedAddressSpace", wintypes.BYTE),
        ("ReadImageFileExecOptions", wintypes.BYTE),
        ("BeingDebugged", wintypes.BYTE),
        ("SpareBool", wintypes.BYTE),
        ("Mutant", wintypes.HANDLE),
        ("ImageBaseAddress", wintypes.LPVOID),
        ("Ldr", wintypes.LPVOID),
        ("ProcessParameters", wintypes.LPVOID),
        ("SubSystemData", wintypes.LPVOID),
        ("ProcessHeap", wintypes.HANDLE),
        ("FastPebLock", wintypes.LPVOID),
        ("FastPebLockRoutine", wintypes.LPVOID),
        ("FastPebUnlockRoutine", wintypes.LPVOID),
        ("EnvironmentUpdateCount", wintypes.ULONG),
        ("KernelCallbackTable", wintypes.LPVOID),
        ("SystemReserved", wintypes.ULONG),
        ("FreeList", wintypes.LPVOID),
        ("TlsExpansionCounter", wintypes.ULONG),
        ("TlsBitmap", wintypes.LPVOID),
        ("TlsBitmapBits", wintypes.DWORD * 2),
        ("ReadOnlySharedMemoryBase", wintypes.LPVOID),
        ("ReadOnlySharedMemoryHeap", wintypes.LPVOID),
        ("ReadOnlyStaticServerData", wintypes.LPVOID),
        ("AnsiCodePageData", wintypes.LPVOID),
        ("OemCodePageData", wintypes.LPVOID),
        ("UnicodeCaseTableData", wintypes.LPVOID),
        ("NumberOfProcessors", wintypes.DWORD),
        ("NtGlobalFlag", wintypes.DWORD),
        ("CriticalSectionTimeout", LARGE_INTEGER),
        ("HeapSegmentReserve", wintypes.DWORD),
        ("HeapSegmentCommit", wintypes.DWORD),
        ("HeapDeCommitTotalFreeThreshold", wintypes.DWORD),
        ("HeapDeCommitFreeBlockThreshold", wintypes.DWORD),
        ("NumberOfHeaps", wintypes.DWORD),
        ("MaximumNumberOfHeaps", wintypes.DWORD),
        ("ProcessHeaps", wintypes.LPVOID),
        ("GdiSharedHandleTable", wintypes.LPVOID),
        ("ProcessStarterHelper", wintypes.LPVOID),
        ("GdiDCAttributeList", wintypes.DWORD),
        ("LoaderLock", wintypes.LPVOID),
        ("OSMajorVersion", wintypes.DWORD),
        ("OSMinorVersion", wintypes.DWORD),
        ("OSBuildNumber", wintypes.WORD),
        ("OSCSDVersion", wintypes.WORD),
        ("OSPlatformId", wintypes.DWORD),
        ("ImageSubsystem", wintypes.DWORD),
        ("ImageSubsystemMajorVersion", wintypes.DWORD),
        ("ImageSubsystemMinorVersion", wintypes.DWORD),
        ("ImageProcessAffinityMask", wintypes.DWORD),
        ("GdiHandleBuffer", wintypes.DWORD * 34),
        ("PostProcessInitRoutine", wintypes.LPVOID),
        ("TlsExpansionBitmap", wintypes.LPVOID),
        ("TlsExpansionBitmapBits", wintypes.DWORD * 32),
        ("SessionId", wintypes.DWORD),
        ("AppCompatFlags", ULARGE_INTEGER),
        ("AppCompatFlagsUser", ULARGE_INTEGER),
        ("pShimData", wintypes.LPVOID),
        ("AppCompatInfo", wintypes.LPVOID),
        ("CSDVersion", UNICODE_STRING),
        ("ActivationContextData", wintypes.LPVOID),
        ("ProcessAssemblyStorageMap", wintypes.LPVOID),
        ("SystemDefaultActivationContextData", wintypes.LPVOID),
        ("SystemAssemblyStorageMap", wintypes.LPVOID),
        ("MinimumStackCommit", wintypes.DWORD)
    ]

# 64位PEB结构
class PEB64(ctypes.Structure):
    _fields_ = [
        ("InheritedAddressSpace", wintypes.BYTE),
        ("ReadImageFileExecOptions", wintypes.BYTE),
        ("BeingDebugged", wintypes.BYTE),
        ("BitField", wintypes.BYTE),
        ("Mutant", wintypes.HANDLE),
        ("ImageBaseAddress", wintypes.LPVOID),
        ("Ldr", wintypes.LPVOID),
        ("ProcessParameters", wintypes.LPVOID),
        ("SubSystemData", wintypes.LPVOID),
        ("ProcessHeap", wintypes.HANDLE),
        ("FastPebLock", wintypes.LPVOID),
        ("AtlThunkSListPtr", wintypes.LPVOID),
        ("IFEOKey", wintypes.LPVOID),
        ("CrossProcessFlags", wintypes.DWORD),
        ("KernelCallbackTable", wintypes.LPVOID),
        ("SystemReserved", wintypes.DWORD),
        ("AtlThunkSListPtr32", wintypes.DWORD),
        ("ApiSetMap", wintypes.LPVOID),
        ("TlsExpansionCounter", wintypes.DWORD),
        ("TlsBitmap", wintypes.LPVOID),
        ("TlsBitmapBits", wintypes.DWORD * 2),
        ("ReadOnlySharedMemoryBase", wintypes.LPVOID),
        ("HotpatchInformation", wintypes.LPVOID),
        ("ReadOnlyStaticServerData", wintypes.LPVOID),
        ("AnsiCodePageData", wintypes.LPVOID),
        ("OemCodePageData", wintypes.LPVOID),
        ("UnicodeCaseTableData", wintypes.LPVOID),
        ("NumberOfProcessors", wintypes.DWORD),
        ("NtGlobalFlag", wintypes.DWORD),
        ("CriticalSectionTimeout", LARGE_INTEGER),
        ("HeapSegmentReserve", wintypes.DWORD),
        ("HeapSegmentCommit", wintypes.DWORD),
        ("HeapDeCommitTotalFreeThreshold", wintypes.DWORD),
        ("HeapDeCommitFreeBlockThreshold", wintypes.DWORD),
        ("NumberOfHeaps", wintypes.DWORD),
        ("MaximumNumberOfHeaps", wintypes.DWORD),
        ("ProcessHeaps", wintypes.LPVOID),
        ("GdiSharedHandleTable", wintypes.LPVOID),
        ("ProcessStarterHelper", wintypes.LPVOID),
        ("GdiDCAttributeList", wintypes.DWORD),
        ("LoaderLock", wintypes.LPVOID),
        ("OSMajorVersion", wintypes.DWORD),
        ("OSMinorVersion", wintypes.DWORD),
        ("OSBuildNumber", wintypes.WORD),
        ("OSCSDVersion", wintypes.WORD),
        ("OSPlatformId", wintypes.DWORD),
        ("ImageSubsystem", wintypes.DWORD),
        ("ImageSubsystemMajorVersion", wintypes.DWORD),
        ("ImageSubsystemMinorVersion", wintypes.DWORD),
        ("ActiveProcessAffinityMask", wintypes.DWORD),
        ("GdiHandleBuffer", wintypes.DWORD * 34),
        ("PostProcessInitRoutine", wintypes.LPVOID),
        ("TlsExpansionBitmap", wintypes.LPVOID),
        ("TlsExpansionBitmapBits", wintypes.DWORD * 32),
        ("SessionId", wintypes.DWORD),
        ("AppCompatFlags", ULARGE_INTEGER),
        ("AppCompatFlagsUser", ULARGE_INTEGER),
        ("pShimData", wintypes.LPVOID),
        ("AppCompatInfo", wintypes.LPVOID),
        ("CSDVersion", UNICODE_STRING),
        ("ActivationContextData", wintypes.LPVOID),
        ("ProcessAssemblyStorageMap", wintypes.LPVOID),
        ("SystemDefaultActivationContextData", wintypes.LPVOID),
        ("SystemAssemblyStorageMap", wintypes.LPVOID),
        ("MinimumStackCommit", wintypes.DWORD),
        ("FlsCallback", wintypes.LPVOID),
        ("FlsListHead", LIST_ENTRY),
        ("FlsBitmap", wintypes.LPVOID),
        ("FlsBitmapBits", wintypes.DWORD * 4),
        ("FlsHighIndex", wintypes.DWORD),
        ("WerRegistrationData", wintypes.LPVOID),
        ("WerShipAssertPtr", wintypes.LPVOID),
        ("pContextData", wintypes.LPVOID),
        ("pImageHeaderHash", wintypes.LPVOID),
        ("TracingFlags", wintypes.DWORD)
    ]

# 定义PROCESS_BASIC_INFORMATION结构
class PROCESS_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("ExitStatus", wintypes.LONG),
        ("PebBaseAddress", ctypes.c_void_p),
        ("AffinityMask", ctypes.c_void_p),
        ("BasePriority", wintypes.LONG),
        ("UniqueProcessId", ctypes.c_void_p),
        ("InheritedFromUniqueProcessId", ctypes.c_void_p)
    ]

# 定义NtQueryInformationProcess函数
def get_peb():
    """使用NtQueryInformationProcess获取当前进程的PEB指针"""
    import warnings
    warnings.warn(
        """Different versions of PEB may be subject to change.
        So please note that you may get an error or get the wrong PEB address.""",
        PEBWarning,
        stacklevel=2
    )
    if sys.platform != "win32":
        raise OSError("This function is only available on Windows")
    
    # 加载ntdll.dll
    ntdll = ctypes.WinDLL('ntdll')
    
    # 定义NtQueryInformationProcess函数原型
    NTSTATUS = wintypes.LONG
    ntdll.NtQueryInformationProcess.argtypes = [
        wintypes.HANDLE,  # ProcessHandle
        wintypes.ULONG,   # ProcessInformationClass
        wintypes.LPVOID,  # ProcessInformation
        wintypes.ULONG,   # ProcessInformationLength
        wintypes.PULONG   # ReturnLength
    ]
    ntdll.NtQueryInformationProcess.restype = NTSTATUS
    
    # 获取当前进程句柄
    current_process = ctypes.windll.kernel32.GetCurrentProcess()
    
    # 查询进程基本信息
    pbi = PROCESS_BASIC_INFORMATION()
    return_length = wintypes.ULONG()
    status = ntdll.NtQueryInformationProcess(
        current_process,  # 当前进程句柄
        0,                # ProcessBasicInformation
        ctypes.byref(pbi),
        ctypes.sizeof(pbi),
        ctypes.byref(return_length)
    )
    
    # 检查状态
    if status != 0:
        raise ctypes.WinError(ctypes.get_last_error())
    
    # 根据架构返回正确的PEB指针
    if ctypes.sizeof(ctypes.c_void_p) == 4:
        return ctypes.cast(pbi.PebBaseAddress, ctypes.POINTER(PEB32))
    else:
        return ctypes.cast(pbi.PebBaseAddress, ctypes.POINTER(PEB64))

# 使用示例
if __name__ == "__main__":
    try:
        peb_ptr = get_peb()
        peb = peb_ptr.contents
        
        # 打印基本信息
        print(f"PEB Address: {ctypes.addressof(peb_ptr.contents)}")
        print(f"BeingDebugged: {peb.BeingDebugged}")
        print(f"ImageBaseAddress: 0x{peb.ImageBaseAddress:x}")
        
        # 检查操作系统版本字段是否存在
        if hasattr(peb, 'OSMajorVersion'):
            print(f"OSVersion: {peb.OSMajorVersion}.{peb.OSMinorVersion}")
        
        # 检查是否处于调试状态
        if peb.BeingDebugged:
            print("Warning: Process is being debugged!")
        else:
            print("Process is not being debugged.")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()