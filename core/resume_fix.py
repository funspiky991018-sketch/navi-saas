import re

def improve_line(line: str):
    text = line.strip()

    if not re.match(r"^(built|developed|created|designed|implemented)", text.lower()):
        text = "Developed " + text

    return text