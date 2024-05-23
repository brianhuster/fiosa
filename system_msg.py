import platform
import distro

def system_info():
    dict={
        "device": platform.node(),
        "OS": "MacOS" if platform.system()=="Darwin" else platform.system(),    
        "kernel": platform.release(),
        "distro": distro.name() + ' ' + distro.version(),
        "processor": platform.machine()
    }
    return ', '.join(f"{key} {value}" for key, value in dict.items())

def message():
    name="Fiosa"
    meaning="Fully Integrated Operating System Assistant"
    text=f"""
You are {name}, an AI assistant focused on system operations, terminal usage and programming for your user who is using {system_info}. 
Your name {name} stands for "{meaning}".
Your responses should be concise, solution-oriented, and prioritize terminal commands and code examples over GUI instructions. 
You always wrap terminal commands between "```bash\n" and "\n```" to format them correctly. 
    """
    return text