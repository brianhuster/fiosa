from llama_cpp import Llama
import subprocess
import re
import time
import sys
import os
import signal
from termcolor import colored
import inquirer
import pyperclip
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
A và B hãy cùng có một cuộc trò chuyện thú vị về trí tuệ nhân tạo và ảnh hưởng của nó đến xã hội loài người. 
    """
    return text

def select(question, options):
    questions = [
        inquirer.List('choice',
                      message=question,
                      choices=options,
                  ),
    ]
    answers = inquirer.prompt(questions)
    return answers['choice']

def print_stream(text, delay=0.05):
    for letter in text:
        print(letter, end='', flush=True)
        time.sleep(delay) 

def calculate(user_input):
    expression=re.findall(r'\d+(?:\.\d+)?(?:[+\-*/]\d+(?:\.\d+)?)*', user_input)
    results=[]
    if not expression:
        return None
    for exp in expression:
        results.append(f"{exp} = {eval(exp)}")
    return ', '.join(results)

def handle_commands(A_output):
    commands = re.findall(r'```bash\n(.*?)\n```', A_output, re.DOTALL)
    for command in commands:
        if '\n' in command:
            commands.remove(command)
            commands.extend(command.split('\n'))
    if commands:
        question = "Do you want to execute the command" + ('s' if  len(commands)>1 else '') + " that I suggested?"
        options = ["Let me see each command and decide", "Yes, execute all commands", "No, continue the chat"]
        choice = select(question, options)
        if choice == options[0]:
            for command in commands:
                subOptions=["Yes, but not allow AI to read output and error", "Yes, and also allow AI to read output and error", "No, just copy command to clipboard", "No, just skip this command"]
                subChoice=select("Do you want to execute the command "+colored(command, 'yellow')+"?", subOptions)
                if subChoice == subOptions[0] or subChoice == subOptions[1]:
                    run_shell(command)
                    if subChoice == subOptions[1]:
                        messages.append({"role": "user", "content": run_shell(command)})
                elif subChoice == subOptions[2]:
                    print("Command copied to clipboard")
                    pyperclip.copy(command)
                else:
                    print("Command skipped")

        elif choice == options[1]:
            for command in commands:
                run_shell(command)      

def run_shell(command):
    try:
        run_shell = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output=f"Output of the command `{command}` is : \n```\n{run_shell.stdout}\n```"
        print(f"\t{output}")
        return output
    except subprocess.CalledProcessError as e:
        error=f"Command `{command}` causes error : \n```\n{run_shell.stderr}\n```"
        print(f"\t{error}")
        return error

def exitProgram():
    print("Exiting the program...")
    llm.reset()
    llm.set_cache(None)
    llm = None
    del llm
    llm = None
    sys.exit()

logo="""
 _____ _                 
|  ___(_) ___  ___  __ _ 
| |_  | |/ _ \/ __|/ _` |
|  _| | | (_) \__ \ (_| |
|_|   |_|\___/|___/\__,_|
"""

def handle_sigtstp(signum, frame):
    exitProgram()

# Register the signal handler for SIGTSTP
signal.signal(signal.SIGTSTP, handle_sigtstp)

# Save the original stderr
original_stderr = sys.stderr

# Redirect stderr to the null device
sys.stderr = open(os.devnull, 'w')

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
    model_path="./models/vinallama-2.7b-chat_q5_0.gguf",  
    n_threads=4,  # The number of CPU threads to use, tailor to your system and the resulting performance. It is double the number of cores in your CPU.
    temperature=0.5,  # The temperature of the model, controlling the randomness of the output
    top_p=0.5,  # The nucleus sampling parameter, controlling the diversity of the output
    n_gpu_layers=35,  # The number of layers to offload to GPU, if you have GPU acceleration available
    n_ctx=4096,  # The maximum context length to use
    do_sample=True,
    use_cache=True,
    top_k=100,
)

# Restore stderr
sys.stderr = original_stderr

# Initialize the chat
messages = [
        {"role": "A", "content": "Bạn có biết về ngành học công nghệ giáo dục không? Mình thấy lĩnh vực này rất thú vị và đang phát triển mạnh mẽ."},
        {"role": "B", "content": "Có, mình biết về ngành học công nghệ giáo dục. Ngành này kết hợp giữa công nghệ thông tin và sư phạm nhằm tạo ra trải nghiệm học tập tốt hơn cho học sinh, giúp học sinh đạt kết quả tốt hơn. Bạn nghĩ sao về tiềm năng của ngành?"},
]

print(colored(logo, 'cyan'))
print(colored("Fiosa:", "green"), "I am Fiosa, your Fully Integrated Operaing System Assistant. I'm powered by AI, so surprises and mistakes are possible. Make sure to verify any generated code or suggestions before using them. How can I help you today?")
print(colored("Note : You can press Ctrl+C to interrupt AI response, Ctrl+D or Ctrl+Z to exit the chat.", 'yellow'))

while True:
    A_output = ''
    B_output = ''
    try:
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        print(colored("A: ", 'blue'), end="")
        output = llm.create_chat_completion(messages=messages, stream=True)
        for chunk in output:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                A_output += delta['content']
                print_stream(delta['content'])
        print("\n")

        messages.append({"role": "A", "content": A_input})

        # bot response
        print(colored("B: ", 'green'), end="")
        output = llm.create_chat_completion(messages=messages, stream=True)
        for chunk in output:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                B_output += delta['content']
                print_stream(delta['content'])
        print("\n")
        sys.stderr = original_stderr

        messages.append({"role": "B", "content": assistant_output})
        
    except (KeyboardInterrupt):
        print('\n')
        handle_commands(A_output)
        continue

    except (EOFError):
        exitProgram()
