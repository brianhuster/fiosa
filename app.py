from llama_cpp import Llama
import subprocess
import re
import time
import platform
import sys
import os
import distro
from termcolor import colored
import inquirer
import pyperclip

def select(question, options):
    questions = [
        inquirer.List('choice',
                      message=question,
                      choices=options,
                  ),
    ]
    answers = inquirer.prompt(questions)
    return answers['choice']

def print_stream(text):
    for letter in text:
        print(letter, end='', flush=True)
        time.sleep(0.05) 

def system_info(): 
    dict={
        "device": platform.node(),
        "OS": "MacOS" if platform.system()=="Darwin" else platform.system(),    
        "kernel": platform.release(),
        "distro": distro.name() + ' ' + distro.version(),
        "processor": platform.machine()
    }
    return ', '.join(f"{key} '{value}'" for key, value in dict.items())


# Save the original stderr
original_stderr = sys.stderr

# Redirect stderr to the null device
sys.stderr = open(os.devnull, 'w')

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
    model_path="./models/stable-code-3b-q4_k_m.gguf",  
    n_threads=4,  # The number of CPU threads to use, tailor to your system and the resulting performance. It is double the number of cores in your CPU.
    temperature=0.5,  # The temperature of the model, controlling the randomness of the output
    top_p=0.5,  # The nucleus sampling parameter, controlling the diversity of the output
    n_gpu_layers=32,  # The number of layers to offload to GPU, if you have GPU acceleration available
    chat_format="llama-2",  # Set the chat format according to the model you are using
    n_ctx=4096,  # The maximum context length to use
    top_k=100,
    do_sample=True,
    use_cache=True,
)

# Restore stderr
sys.stderr = original_stderr

# Initialize the chat
messages = [
        {"role": "system", "content": f"You are a helpful AI assistant for your user who is using {system_info()}. You tend to respond briefly and straight to the point. You don't explain much. You prefer terminal to GUI. You always tag terminal command as 'bash', for example '```bash\nls -l\n```'."},
]


print("Welcome to the chat! You can start chatting with the AI assistant.\nNote : You can press Ctrl+C to interrupt AI response, Ctrl+D to exit the chat.")

while True:
    try:
        user_input = input(colored("You: ", 'green'))
        messages.append({"role": "user", "content": user_input})
        print(colored("Assistant: ", 'green'), end="")
        print_stream("Please wait, I am thinking...")
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        output = llm.create_chat_completion(messages=messages, stream=True)
        assistant_output = ""
        for chunk in output:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                assistant_output += delta['content']
                print_stream(delta['content'])
        # Print out each letter one by one
        print()  # Print a newline at the end
        sys.stderr = original_stderr

        messages.append({"role": "assistant", "content": assistant_output})
        # Check if the output contains a command line
        commands = re.findall(r'```(?:bash)?\n(.*?)\n```', assistant_output, re.DOTALL)
        if commands:
            question = "Do you want to execute the command" + ('s' if  len(commands)>1 else '') + "that I suggested?"
            options = ["Let me see each command and decide", "Yes, execute all commands", "No, continue the chat"]
            choice = select(question, options)
            if choice == options[0]:
                for command in commands:
                    subOptions=["Yes", "Yes, but also allow AI to see the output and error after running the command", "No, just copy command to clipboard", "No, just skip this command"]
                    subChoice=select("Do you want to execute the command "+colored(command, 'yellow')+"?", subOptions)
                    if subChoice == subOptions[0] or subChoice == subOptions[1]:
                        run_shell = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if subChoice == subOptions[1]:
                            messages.append({"role": "terminal", "content": f"Output of the command {command} :\n{run_shell.stdout}\n{run_shell.stderr}"})
                            print(messages)
                    else:
                        if subChoice == subOptions[2]:
                            print("Command copied to clipboard")
                            pyperclip.copy(command)
                        else:
                            print("Command skipped")

            elif choice == options[1]:
                for command in commands:
                    subprocess.run(command, shell=True, check=True)
            else:
                continue

    except (KeyboardInterrupt):
        print('\n')
        continue

    except (EOFError):
        print("\nExiting the chat...")
        break
        exit(0)
