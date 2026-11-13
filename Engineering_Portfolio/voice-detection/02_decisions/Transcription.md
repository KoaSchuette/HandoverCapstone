# Voice Recognition and Transcription

## Speech Recognition Library

**Decision:** Use faster-whisper for local speech-to-text transcription.

### Context

The robot requires a speech recognition system to transcribe spoken commands into text for triggering of task execution. The system should be reasonably accurate, responsive, and ideally capable of operating using local computation power of the device.

### Options considered

| Option | For | Against |
|---|---|---|
| OpenAI Whisper | Established, accurate, multiple model sizes | Higher computational requirements |
| faster-whisper (chosen) | Faster, multiple model sizes, equally easy implementation | Additional dependencies |
| Cloud-based recognition | Offloads processing | Requires internet, external service dependency |

Faster-whisper was selected for its efficient local transcription, allowing responsive speech recognition without relying on cloud services. There were other options, like the OpenAI Whisper, but this seemed to provide the best balance of speed and precision. If the library ran into issues, the project could explore other options as it is a fairly modular component.

## Model Selection

**Decision:** Initially use the Small model. Complete further testing on viability of Tiny/Medium models as an alternative, once functionality ported. Remove Large models from consideration.

Different Whisper model sizes were tested to compare transcription quality and processing time.

| Model | Approximate transcription time | Observations |
|---|---|---|
| Tiny / Base | Under 0.75 s | Very fast, lower accuracy |
| Small | ~2-2.5 s | Good balance of speed and accuracy |
| Medium | ~4–5 s | Slightly improved recognition in testing |
| Large-v3 | 5+ s | Mismatch in computational requirements |

*Times are from preliminary testing using developer CPU-based measurements. Testing primarily used 5-second recordings, but length of recording did not appear to greatly impact the transcription time (3 s vs 15 s).*

The Small model was initially selected for its balance between speed and accuracy. Medium remains under consideration depending on the computational resources available on the final hardware.

## Audio Capture and Processing

**Decision:** Use `sounddevice` until issues arise, with fixed 5-second audio chunks and queue-based processing.

### Context

Initial testing used 15-second recordings, with delayed transcription results. This was reduced to continuous 5-second chunks to improve responsiveness.

Audio is captured continuously at 16 kHz using `sounddevice.InputStream`, buffered through a queue, and passed to faster-whisper for transcription.

The file has gone through (currently) three iterations:
- voice.py: faster-whisper on pre-recorded audio file
- voice_live.py: recording of fixed-length audio file using sounddevice, transcribing once recording ended.
- voice_stream.py (**current**): Audio captured continuously, processed in fixed-length buffers via a queue.

### Limitations and improvements

Fixed-duration chunks simplified implementation but may split spoken commands between recordings. A more responsive system will split more commands, putting the two most important factors at odds. Additionally, silence is processed even when no speech is present.

**Voice Activity Detection (VAD)** is being considered to identify speech boundaries, reduce unnecessary processing, and improve the handling of commands of varying lengths. In general, the next step is a more dynamic recording and transcription approach.

Implementation with a small LLM is expected, with the LLM interpreting the transcribed output into robot task commands without the need to scan for a specific phrase.

## Reflection

The initial implementation established a working local speech-to-text pipeline and provided preliminary comparisons of model performance. Establishing this proof of concept enabled understanding of the tunable parameters (beam size, microphone selection), potential implementation challenges, and ballpark performance numbers like estimated transcription time.

The 5-second chunk approach offered a simple starting point, but its limitations highlight the potential benefits of more dynamic, possibly VAD-based segmentation. Further development will focus on improving speech handling and integrating transcription into the ROS 2 architecture. Finally, completing more formal testing to establish if the implemented system can be tuned further.