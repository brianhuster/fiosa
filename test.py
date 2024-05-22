import re

assistant_output = "```bash\nsudo iwconfig wlan0 ssid \"Your_SSID_Here\"\n```"
commands = re.findall(r'```(?:bash)?\n(.*?)\n```', assistant_output, re.DOTALL)

print(commands)  # Outputs: ['sudo iwconfig wlan0 ssid "Your_SSID_Here"']