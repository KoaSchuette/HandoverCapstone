import re

def normalise(text: str) -> str:
    """Fix known speech-recognition mistakes before anything else sees the text."""
    return re.sub(r"\bread\b", "red", text, flags=re.IGNORECASE)

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