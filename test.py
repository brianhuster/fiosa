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


def print_stream(text, delay=0.05):
    for letter in text:
        print(letter, end='', flush=True)
        time.sleep(delay) 


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
    model_path="./models/Phi-3-mini-4k-instruct-q4.gguf",  # The path to the model file
    n_threads=4,  # The number of CPU threads to use, tailor to your system and the resulting performance. It is double the number of cores in your CPU.
    temperature=0.5,  # The temperature of the model, controlling the randomness of the output
    top_p=0.5,  # The nucleus sampling parameter, controlling the diversity of the output
    n_gpu_layers=35,  # The number of layers to offload to GPU, if you have GPU acceleration available
    n_ctx=4096,  # The maximum context length to use
    do_sample=True,
    use_cache=True,
    top_k=100,
)

def exitProgram():
    print("\nExiting the program...")
    llm.reset()
    llm.set_cache(None)
    llm = None
    del llm
    llm = None
    sys.exit()

# Restore stderr
sys.stderr = original_stderr

# Initialize the chat
messages = [
        {"role": "user", "content": "I love Ubuntu"},
]

print(colored(logo, 'cyan'))
print(colored("Fiosa:", "green"), "I am Fiosa, your Fully Integrated Operaing System Assistant. I'm powered by AI, so surprises and mistakes are possible. Make sure to verify any generated code or suggestions before using them. How can I help you today?")
print(colored("Note : You can press Ctrl+C to interrupt AI response, Ctrl+D or Ctrl+Z to exit the chat.", 'yellow'))

while True:
    A_output = ''
    B_output = ''
    try:
        # original_stderr = sys.stderr
        # sys.stderr = open(os.devnull, 'w')
        print(colored("A: ", 'blue'), end="")
        output = llm.create_chat_completion(messages=messages, stream=True)
        for chunk in output:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                A_output += delta['content']
                print_stream(delta['content'])
        print("\n")

        messages.append({"role": "assistant", "content": A_output})

        # bot response
        print(colored("B: ", 'green'), end="")
        output = llm.create_chat_completion(messages=messages, stream=True)
        for chunk in output:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                B_output += delta['content']
                print_stream(delta['content'])
        print("\n")
        # sys.stderr = original_stderr

        messages.append({"role": "user", "content": B_output})
        
    
    except (EOFError):
        exitProgram()
