import platform
import distro

system_info = {
    "device": platform.node(),
    "OS": platform.system(),    
    "kernel": platform.release(),
    "distro": distro.name() + ' ' + distro.version(),
    "processor": platform.machine()
}

for key, value in system_info.items():
    print(f"{key}: {value}")
