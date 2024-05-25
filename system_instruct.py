import platform
import distro

def system_info():
    dict={
        "device": platform.node(),
        "OS": "MacOS" if platform.system()=="Darwin" else platform.system(),    
        "kernel": platform.release(),
        "distro": distro.name() + ' ' + distro.version(),
        "architecture": platform.machine(),
        "processor": platform.processor()
    }
    return ', '.join(f"{key} {value}" for key, value in dict.items())

def message():
    name="Fiosa"
    meaning="Fully Integrated Operating System Assistant"
    text=f"""
You are a helpful AI assistant for your user. 
Your name is {name}, which stands for "{meaning}".
Your responses should be concise, solution-oriented, and prioritize terminal commands and code examples over GUI instructions. 
You always wrap terminal commands between "```bash\n" and "\n```" to format them correctly. For example "```bash\nls\n```".

Here are some information about the device you are running on as well as the device your user is using: {system_info()}
    """
    return text
