import re

def calculate(user_input):
    expression=re.findall(r'\d+(?:\.\d+)?(?:[+\-*/]\d+(?:\.\d+)?)*', user_input)
    results=[]
    if not expression:
        return None
        for exp in expression:
            results.append(f"{exp} = {eval(exp)}")
    return ', '.join(results)

print(calculate("Calcucate 247*768"))
