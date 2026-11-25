# Command Parser (local LLM)

Turns the text of a spoken command into a structured command for the robot, using a small language model that runs on your own machine (no internet needed after setup).

```
mic -> VAD clip -> Whisper text -> command_parser.py -> controller.py -> (function_code, subject_code)
                                    (local LLM)         (checks + voice on/off state)
```

Example: `"Pass me the green screwdriver"` -> `deliver_tool, green_screwdriver` -> `(3, 2)`

Requirements: R1 (delivery and return in 15 s or less, target 5 s) and R5 (correct tool in at least 96% of attempts).

## Quick start

You need three things: **Ollama** (runs the model), the **model** (`qwen2.5:3b`, about 2 GB, downloaded once) and the **`ollama` Python package**. Any OS works.

| Step | macOS | Windows | Linux |
|---|---|---|---|
| 1. Install Ollama | `brew install ollama` or the app from ollama.com | Installer from ollama.com/download | `curl -fsSL https://ollama.com/install.sh \| sh` |
| 2. Make sure it is running | `brew services start ollama` (the app starts it itself) | Starts in the background after install | Usually a service already, otherwise `ollama serve` |

Then, on every OS (with your Python environment active):

```bash
ollama pull qwen2.5:3b
pip install ollama
python test_parser.py        # runs the test table
```

Check the server is up by opening `http://localhost:11434` in a browser. It should say "Ollama is running".

### Running in the dev container
The parser only needs text, so it works in the dev container. The one decision is where Ollama runs.

- **Ollama on your computer (faster on Mac and Windows).** Point the container at it with an environment variable, for example in `devcontainer.json` under `remoteEnv`: `"OLLAMA_HOST": "http://host.docker.internal:11434"`. On a Linux host, Ollama must also listen on all interfaces (`OLLAMA_HOST=0.0.0.0 ollama serve`) and the container needs `--add-host=host.docker.internal:host-gateway` in `runArgs`.
- **Ollama inside the container (self-contained).** Install it with the Linux command above, start it with `ollama serve &`, then `ollama pull qwen2.5:3b`. On Mac and Windows hosts the container normally has no GPU access, so expect slower parsing.

Add `ollama` to `requirements.txt` so the container installs the Python package automatically.

## Using it

```python
from command_parser import parse_command
from controller import Controller

controller = Controller()          # create once: it remembers whether voice is on or off
parse_command("warm up")           # first call loads the model (slow), so do it at startup

# for each transcript produced by the speech-to-text stage:
cmd, secs = parse_command(text)    # {'function': 'deliver_tool', 'subject': 'blue_screwdriver'}
result = controller.handle(cmd, text)

if result is None:
    print("ignored (voice is deactivated)")
else:
    function_code, subject_code = result
    print(f"send to robot: {function_code}, {subject_code}  (parsed in {secs:.2f} s)")
```

One-off check from a terminal:
```bash
python -c "import command_parser; print(command_parser.parse_command('pass me the green screwdriver'))"
```

## Files

| File | What it does |
|---|---|
| `commands.py` | The vocabulary: names and numeric codes for every function and tool. Edit this to change commands, tools or codes |
| `command_parser.py` | The only file that talks to the LLM. `parse_command(text)` returns `(command, seconds)`. The system prompt and its examples define what each command means |
| `controller.py` | Checks the LLM's answer, keeps the voice on/off state, and converts names to codes |
| `test_cases.py` | Test phrases with expected results, grouped by category |
| `test_parser.py` | Runs the test cases and prints accuracy, failures by severity, and timing |
| `DEVELOPMENT_LOG.md` | How the parser was built: results of each run, what failed and why |

## Commands

| Function | Code | Meaning | Example |
|---|---|---|---|
| `unknown` | 0 | Not understood, or a delivery with no colour | "what time is it" |
| `deactivate_voice` | 1 | Ignore task commands until reactivated | "voice off" |
| `reactivate_voice` | 2 | Listen to task commands again | "voice on" |
| `deliver_tool` | 3 | Hand over a screwdriver (colour required) | "pass me the green screwdriver" |
| `cancel_task` | 4 | Abandon the current task | "never mind" |
| `pause_task` | 5 | Pause the current task | "hold on" |
| `resume_task` | 6 | Continue a paused task | "carry on" |

Tools: `none` (0), `red_screwdriver` (1), `green_screwdriver` (2), `blue_screwdriver` (3). Only `deliver_tool` has a tool; everything else gets `none`.



## Test results

Model `qwen2.5:3b`, 80 test phrases:

| Metric | Result |
|---|---|
| Accuracy | 78/80 (98%) |
| Wrong or false deliveries | 0 |
| Parse time (mean / max) | 0.43 s / 0.57 s, on a MacBook (Apple Silicon) |

Known failures: "I dropped the red screwdriver" is read as `cancel_task`, and "keep going" is missed.

**Read these numbers carefully.** The prompt was tuned using these same 80 phrases, so 98% is optimistic. It covers the parser only, not speech-to-text, and timings depend on your hardware, so run `test_parser.py` on your own machine. The R5 result needs a fresh test set and real recorded speech. See `DEVELOPMENT_LOG.md` for details.

## Changing the model

Change `MODEL` in `command_parser.py`, run `ollama pull <name>`, and re-run `test_parser.py` to compare, for example `qwen2.5:7b` or `llama3.2:3b`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Connection error | Ollama is not running (or, in the dev container, `OLLAMA_HOST` is not set or reachable) |
| `model not found` | `ollama pull qwen2.5:3b` |
| First call is slow | The model is loading. Make one warm-up call at startup |
| `ModuleNotFoundError: ollama` | Activate the right Python environment and `pip install ollama` |
| Different output for the same input | `temperature` must stay 0 in `command_parser.py` |