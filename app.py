from llama_cpp import Llama
import subprocess
import re
import time
import distro
import sys
import os
from termcolor import colored
import inquirer

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

# Save the original stderr
original_stderr = sys.stderr

# Redirect stderr to the null device
sys.stderr = open(os.devnull, 'w')

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
    model_path="./models/stable-code-3b-q4_k_m.gguf",  # Download the model file firThinking time, # The max sequence length to use - note that longer sequence lengths require much more resources
    n_threads=4,  # The number of CPU threads to use, tailor to your system and the resulting performance
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
distroName=distro.name()
distroVer=distro.version()
messages = [
    {"role": "system", "content": f"You are a helpful and polite assistant for {distroName} {distroVer} users. You tend to respond briefly and straight to the point. You prefer terminal to GUI. You tag terminal command as 'bash', for example '```bash\nls -l\n```'."},
]

print("Welcome to the chat! You can start chatting with the AI assistant.")

try:
    while True:
        user_input = input(colored("You: ", 'green'))
        messages.append({"role": "user", "content": user_input})
        print(colored("Assistant: ", 'green') + "Please wait, I am thinking...")
        original_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')
        output = llm.create_chat_completion(messages=messages, stream=True)
        assistant_output = ""
        sys.stderr = original_stderr
        for chunk in output:
            delta = chunk['choices'][0]['delta']
            if 'content' in delta:
                assistant_output += delta['content']
                print_stream(delta['content'])
        # Print out each letter one by one
        print()  # Print a newline at the end

        messages.append({"role": "assistant", "content": assistant_output})
        # Check if the output contains a command line
        commands = re.findall(r'```(?:bash)?\n(.*?)\n```', assistant_output, re.DOTALL)
        if commands:
            question = "Do you want to execute the command" + ('s' if  len(commands)>1 else '') + "that I suggested?"
            options = ["Let me see each command and decide", "Yes, execute all commands", "No, continue the chat"]
            choice = select(question, options)
            if choice == options[0]:
                for command in commands:
                    subOptions=["Yes", "Yes, but also allow me to see the output and error after running the command", "No, just copy command to clipboard", "No, just skip this command"]
                    subChoice=select("Do you want to execute the command "+colored(command, 'yellow')+"?", subOptions)
                    if subChoice == subOptions[0] or subChoice == subOptions[1]:
                        subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if subChoice == subOptions[1]:
                            messages.append({"role": "terminal", "content": f"{stdout}\n{stderr}"})
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

except (KeyboardInterrupt, EOFError):
    print("\nExiting the chat...")
    exit(0)
