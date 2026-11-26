import re

# Vocabulary
COLOUR_WORDS = {
    "red_screwdriver": {"red"},        # "read" is already turned into "red" by normalise()
    "green_screwdriver": {"green"},
    "blue_screwdriver": {"blue"},
}

FUNCTION_CODES = {
    "unknown": 0,
    "deactivate_voice": 1,
    "reactivate_voice": 2,
    "deliver_tool": 3,
    "cancel_task": 4,
    "pause_task": 5,
    "resume_task": 6,
}

SUBJECT_CODES = {
    "none": 0,
    "red_screwdriver": 1,
    "green_screwdriver": 2,
    "blue_screwdriver": 3,
}

def normalise(text: str) -> str:
    """Fix known speech-recognition mistakes before anything else sees the text."""
    return re.sub(r"\bread\b", "red", text, flags=re.IGNORECASE)

def spoken_colours(text: str) -> set:
    """Which tool colours were actually said in the transcript."""
    words = set(re.findall(r"[a-z]+", normalise(text).lower()))
    return {subject for subject, names in COLOUR_WORDS.items() if words & names}


def validate(cmd: dict, text: str):
    f = cmd.get("function")
    s = cmd.get("subject")
    if f not in FUNCTION_CODES or s not in SUBJECT_CODES:
        return "unknown", "none"
    if f != "deliver_tool":
        s = "none"
    if f == "deliver_tool" and spoken_colours(text) != {s}:   # exactly one colour, and it matches
        return "unknown", "none"
    return f, s

# Voice on/off state

class Controller:
    def __init__(self):
        self.voice_active = True

    def handle(self, cmd: dict, text: str):
        """Return (function_code, subject_code), or None if the command is ignored."""
        f, s = validate(cmd, text)

        if f == "deactivate_voice":
            self.voice_active = False
        elif f == "reactivate_voice":
            self.voice_active = True
        elif not self.voice_active:
            return None          # voice is off: ignore everything except reactivate

        return FUNCTION_CODES[f], SUBJECT_CODES[s]

