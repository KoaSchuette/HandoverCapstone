import json
import time

import ollama

from commands import FUNCTION_CODES, SUBJECT_CODES, normalise

MODEL = "qwen2.5:3b"

# Tells Ollama the exact shape of the output. The model can only produce
# values from these lists, so it can't invent a new command.
SCHEMA = {
    "type": "object",
    "properties": {
        "function": {"type": "string", "enum": list(FUNCTION_CODES)},
        "subject": {"type": "string", "enum": list(SUBJECT_CODES)},
    },
    "required": ["function", "subject"],
}

SYSTEM = """You convert transcribed speech into a command for a robot that hands screwdrivers to a person.
The text comes from speech recognition and can contain mistakes.
The word "read" means the colour red. Treat "read screwdriver" as "red screwdriver".
"screw driver" means "screwdriver".

Functions:
- deactivate_voice: ONLY when the speaker talks about the voice, listening or voice control being turned off (e.g. "voice off", "stop listening", "go to sleep").
- reactivate_voice: ONLY when the speaker talks about the voice or listening being turned back on (e.g. "voice on", "start listening", "wake up").
- deliver_tool: the speaker asks for a screwdriver to be handed to them. The subject is its colour.
- cancel_task: abandon the current task or delivery (e.g. "cancel", "never mind", "forget it", "stop the task").
- pause_task: pause the current task (e.g. "pause", "hold on", "wait").
- resume_task: continue a paused task (e.g. "resume", "continue", "carry on", "go ahead").
- unknown: anything else.


Subject: red_screwdriver, green_screwdriver or blue_screwdriver only for deliver_tool. Otherwise use none.
The colour must be spoken (red, green or blue; "read" counts as red). Never guess a colour.
If no colour is spoken, the function is unknown and the subject is none.

Only choose a function when the speaker is giving an instruction to the robot. Comments, statements and questions are unknown, even if they mention a screwdriver or a colour.

Examples:
"pass me the green screwdriver" -> deliver_tool, green_screwdriver
"can you grab the blue one, the screw driver" -> deliver_tool, blue_screwdriver
"voice off" -> deactivate_voice, none
"never mind" -> cancel_task, none
"what time is it" -> unknown, none
"hand me the read screw driver" -> deliver_tool, red_screwdriver
"I need a screwdriver" -> unknown, none
"okay resume" -> resume_task, none
"carry on" -> resume_task, none
"wait a second" -> pause_task, none
"voice back on" -> reactivate_voice, none
"my red screwdriver is broken" -> unknown, none
"the blue screwdriver is on the shelf" -> unknown, none
"stop the task" -> cancel_task, none
"go ahead" -> resume_task, none
"let's continue" -> resume_task, none
"please go on" -> resume_task, none
"get going again" -> resume_task, none
"carry on with the task" -> resume_task, none
"listen to me again" -> reactivate_voice, none
"give me those" -> unknown, none
"the green screwdriver fell on the floor" -> unknown, none
"she took the blue screwdriver" -> unknown, none
"""


def parse_command(text: str):
    """Returns (command_dict, seconds_taken)."""
    text = normalise(text)
    start = time.perf_counter()
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": text},
        ],
        format=SCHEMA,                 # forces output to match SCHEMA
        options={"temperature": 0},    # 0 = same input gives the same output
        keep_alive="30m",              # keep the model in memory between calls
    )
    elapsed = time.perf_counter() - start

    try:
        cmd = json.loads(response["message"]["content"])
    except (json.JSONDecodeError, KeyError, TypeError):
        cmd = {"function": "unknown", "subject": "none"}
    return cmd, elapsed