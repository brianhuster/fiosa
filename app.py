from llama_cpp import Llama
import subprocess
import re
import time
import sys
import os
from termcolor import colored
import inquirer
import pyperclip
import system_instruct 

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
    expression=re.findall(r'^\d+(?:\.\d+)?(?:[+\-*/]\d+(?:\.\d+)?)*$', user_input)
    results=[]
    if not expression:
        return None
        for exp in expression:
            results.append(f"{exp} = {eval(exp)}")
    return ', '.join(results)

# Save the original stderr
original_stderr = sys.stderr

# Redirect stderr to the null device
sys.stderr = open(os.devnull, 'w')

# Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.
llm = Llama(
    model_path="./models/stable-code-3b-q5_k_m.gguf",  
    n_threads=4,  # The number of CPU threads to use, tailor to your system and the resulting performance. It is double the number of cores in your CPU.
    temperature=0.5,  # The temperature of the model, controlling the randomness of the output
    top_p=0.5,  # The nucleus sampling parameter, controlling the diversity of the output
    n_gpu_layers=35,  # The number of layers to offload to GPU, if you have GPU acceleration available
    chat_format="llama-2",  # Set the chat format according to the model you are using
    n_ctx=4096,  # The maximum context length to use
    do_sample=True,
    use_cache=True,
    top_k=100,
)

# Restore stderr
sys.stderr = original_stderr

# Initialize the chat
messages = [
        {"role": "system", "content": system_instruct.message()},
]

print("Welcome to the chat! You can start chatting with the AI assistant.\nNote : You can press Ctrl+C to interrupt AI response, Ctrl+D to exit the chat.")

while True:
    try:
        user_input = input(colored("You: ", 'green'))
        user_input+="Given that "+calculate(user_input) if calculate(user_input) else ""
        messages.append({"role": "user", "content": user_input})

        # bot response
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
        print("\n")
        sys.stderr = original_stderr

        messages.append({"role": "assistant", "content": assistant_output})
        print(messages)

        # handle output
        # Check if the output contains a command line
        commands = re.findall(r'```(?:bash)?\n(.*?)\n```', assistant_output, re.DOTALL)
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
                    subOptions=["Yes", "Yes, but also allow AI to see the output and error after running the command", "No, just copy command to clipboard", "No, just skip this command"]
                    subChoice=select("Do you want to execute the command "+colored(command, 'yellow')+"?", subOptions)
                    if subChoice == subOptions[0] or subChoice == subOptions[1]:
                        run_shell = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        if subChoice == subOptions[1]:
                            if run_shell.returncode == 0:
                                output=f"Output of the command `{command}` is : \n```\n{run_shell.stdout}\n```"
                                print(f"\t{output}")
                                messages.append({"role": "user", "content": output})
                            else:
                                error=f"Command `{command}` causes error : \n```\n{run_shell.stderr}\n```"
                                print(f"\t{error}")
                                messages.append({"role": "user", "content": error})
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
