# Voice Detection
Voice Detection is the vocal input subsystem. Provides operator the control of verbally issuing a command to the robot. 

Owner: Ryan Henderson

## Status
A Python script which uses sounddevice Python Library to record a constant stream of audio from a selected Microphone. It has currently implemented a fixed-window streaming speech recognition: once 5s of audio is reached in the buffer queue, it is passed to a faster-whisper offline transcription model, with various 'sizes' of models available. The output of the faster-whisper model is printed to the terminal, and output is scanned for key words (ex. If 'Exit Sequence' is detected in the output, the script terminates)

In this stage, until integration next steps are achieved, it is a functional but limited to a proof of concept or intermediary stage relative to the project.

File version progression:
voice.py > voice_live.py > voice_stream.py (current)

## Project Requirements
- R1: Delivery and return each completed in 15 s or less (target 5 s)
- R5: Correct tool picked up in at least 96% of attempts

Response time of this subsystem in processing the command once it is issued verbally must fit within the R1 Completion time requirement. Realistically, it must be designed to not represent a significant portion of the completion time.

This subsystem must reliably parse the verbal command of the operator. The subsystem must be able to robustly determine which colour of tool the operator is requesting.

## What's in this folder

| Folder | Contents |
|---|---|
| [`02_decisions/`](02_decisions/) | [Transcription](02_decisions/Transcription.md), [Interpreter](02_decisions/Interpreter.md) |
| [`04_design/`](04_design/) | Planning document relevant to design decisions or process. |
| [`06_experiments/`](06_experiments/) | Rough preliminary recording, transcription and model testing logs by recording script terminal output |
| [`07_data/`](07_data/) | Miscellaneous audio files used for initial transcription testing  |
| [`08_references/`](02_decisions/) | Websites, Documentation, GitHub links commonly revisited during design |
| Code | [`src/handover_voice/`](https://github.com/KoaSchuette/HandoverCapstone/tree/ffa9aff/src/handover_voice):  |

## Next Steps
- Integration from developer coding environment to ROS2 Node, Windows -> Linux compatibility
- More robust Microphone handling
- Integrating with a small-LLM ROS2 node to dynamically interpret the commands from the operator
- Additional functionality, pivoting from fixed-window recognition to more dynamic methods such as VAD-based segmentation.

