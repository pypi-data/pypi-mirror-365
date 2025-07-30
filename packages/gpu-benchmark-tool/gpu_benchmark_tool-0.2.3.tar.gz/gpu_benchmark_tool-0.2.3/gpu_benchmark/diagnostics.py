"""Diagnostics utilities for GPU Benchmark Tool.

This module provides functions to retrieve GPU information and print temperature thresholds.
"""
import platform
import os
import sys
import subprocess

try:
    import psutil
except ImportError:
    psutil = None

try:
    import cpuinfo
except ImportError:
    cpuinfo = None

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import torch
except ImportError:
    torch = None

# baseline info & thresholds

def get_gpu_info(handle):
    """Gets GPU information such as temperature, power usage, memory, and fan speed.

    Args:
        handle: NVML handle to the GPU.

    Returns:
        dict: Dictionary containing temperature, power usage, memory usage, and fan speed.
    """
    if not PYNVML_AVAILABLE:
        return {
            "Temperature (C)": -1,
            "Power Usage (W)": -1,
            "Memory Used (MB)": -1,
            "Memory Total (MB)": -1,
            "Fan Speed (%)": "Not available"
        }
        
    temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
    power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000
    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    try:
        fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
    except pynvml.NVMLError:
        fan_speed = "Not supported"

    info = {
        "Temperature (C)": temperature,
        "Power Usage (W)": power_usage,
        "Memory Used (MB)": memory_info.used // (1024**2),
        "Memory Total (MB)": memory_info.total // (1024**2),
        "Fan Speed (%)": fan_speed,
    }
    return info

def print_temperature_thresholds(handle):
    """Prints the temperature thresholds for slowdown and shutdown for a GPU.

    Args:
        handle: NVML handle to the GPU.
    """
    if not PYNVML_AVAILABLE:
        print("NVIDIA GPU monitoring not available")
        return
        
    try:
        slowdown = pynvml.nvmlDeviceGetTemperatureThreshold(
            handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN)
        print(f"⚠️  Slowdown Threshold: {slowdown} °C")
    except pynvml.NVMLError as e:
        print(f"Slowdown Threshold: Not supported ({str(e)})")

    try:
        shutdown = pynvml.nvmlDeviceGetTemperatureThreshold(
            handle, pynvml.NVML_TEMPERATURE_THRESHOLD_SHUTDOWN)
        print(f"🔥 Shutdown Threshold: {shutdown} °C")
    except pynvml.NVMLError as e:
        print(f"Shutdown Threshold: Not supported ({str(e)})")

def get_system_info():
    """Gathers baseline system information (CPU, RAM, OS, CUDA, driver, etc).

    Returns:
        dict: Dictionary containing system information.
    """
    info = {}

    # OS
    info["OS"] = platform.platform()

    # CPU
    info["CPU Model"] = platform.processor() or platform.uname().processor or "Unknown"
    info["CPU Cores"] = os.cpu_count() or "Unknown"
    # CPU Frequency
    cpu_freq = None
    if psutil and hasattr(psutil, "cpu_freq"):
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_freq = f"{freq.current:.2f} MHz"
        except Exception:
            pass
    info["CPU Frequency"] = cpu_freq or "Unknown"
    # CPU Maker/Model (detailed)
    if cpuinfo:
        try:
            cpu = cpuinfo.get_cpu_info()
            info["CPU Model"] = cpu.get("brand_raw", info["CPU Model"])
            info["CPU Vendor"] = cpu.get("vendor_id_raw", "Unknown")
        except Exception:
            pass

    # RAM
    ram_gb = None
    if psutil and hasattr(psutil, "virtual_memory"):
        try:
            ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        except Exception:
            pass
    info["RAM Amount"] = f"{ram_gb:.1f} GB" if ram_gb else "Unknown"
    # RAM Speed (platform-specific, best effort)
    ram_speed = "Unknown"
    if sys.platform == "linux" and os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        break  # Already got RAM amount
            # Try dmidecode for speed
            try:
                out = subprocess.check_output(["dmidecode", "--type", "17"], stderr=subprocess.DEVNULL)
                for l in out.decode().splitlines():
                    if "Speed:" in l and "Configured" not in l:
                        ram_speed = l.split(":")[-1].strip()
                        break
            except Exception:
                pass
        except Exception:
            pass
    elif sys.platform == "win32":
        try:
            out = subprocess.check_output(["wmic", "MemoryChip", "get", "Speed"], stderr=subprocess.DEVNULL)
            lines = out.decode().splitlines()
            speeds = [l.strip() for l in lines[1:] if l.strip().isdigit()]
            if speeds:
                ram_speed = f"{max(map(int, speeds))} MHz"
        except Exception:
            pass
    info["RAM Speed"] = ram_speed

    # CUDA version
    cuda_version = None
    if torch and hasattr(torch, "version") and hasattr(torch.version, "cuda"):
        cuda_version = torch.version.cuda
    if not cuda_version and PYNVML_AVAILABLE:
        try:
            v = pynvml.nvmlSystemGetCudaDriverVersion()
            cuda_version = str(v)
        except Exception:
            pass
    info["CUDA Version"] = cuda_version or "Unknown"

    # GPU driver version
    driver_version = None
    if PYNVML_AVAILABLE:
        try:
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            if isinstance(driver_version, bytes):
                driver_version = driver_version.decode()
        except Exception:
            pass
    info["Driver Version"] = driver_version or "Unknown"

    return info


def print_system_info():
    """Prints baseline system information (CPU, RAM, OS, CUDA, driver, etc).

    Returns:
        None
    """
    info = get_system_info()
    print("\nSystem Information:")
    print("-" * 30)
    for key, value in info.items():
        print(f"{key:.<25} {value}")
