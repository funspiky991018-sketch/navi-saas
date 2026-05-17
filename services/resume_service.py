import re


def improve_line(line: str):

    text = line.strip()

    if not re.match(
        r"^(built|developed|created|designed|implemented|led|managed|optimized)",
        text.lower()
    ):
        text = "Developed " + text

    replacements = {
        "worked on": "contributed to",
        "helped": "assisted in improving",
        "made": "developed",
        "did": "executed"
    }

    for k, v in replacements.items():
        text = re.sub(k, v, text, flags=re.IGNORECASE)

    if not re.search(r"\d+%", text):
        text += " with improved efficiency and performance"

    if "api" in text.lower():
        text += " using RESTful API architecture"

    if "data" in text.lower():
        text += " handling structured datasets"

    return text


def improve_resume_lines(resume: str):

    lines = [l.strip() for l in resume.split("\n") if l.strip()]

    improved = []

    for line in lines:
        improved.append({
            "original": line,
            "improved": improve_line(line)
        })

    return {
        "ai_mode": "offline",
        "improved": improved
    }