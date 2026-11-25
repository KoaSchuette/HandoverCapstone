import re

from commands import FUNCTION_CODES, SUBJECT_CODES, normalise

COLOUR_WORDS = {
    "red_screwdriver": {"red"},        # "read" is already turned into "red" by normalise()
    "green_screwdriver": {"green"},
    "blue_screwdriver": {"blue"},
}


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