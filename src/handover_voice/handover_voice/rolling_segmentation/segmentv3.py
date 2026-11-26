import collections
import os
import queue
import wave

import numpy as np
import sounddevice as sd

import time
from faster_whisper import WhisperModel

FS = 16000
BLOCK = 512                 # 32 ms
MIC = None                  # input device number from devices.py (None = system default)

THRESHOLD = 0.008           # between background (0.002) and speech (0.01+)
SILENCE_BLOCKS = 16         # 16 x 32 ms = about 0.5 s of quiet ends a command
PREROLL_BLOCKS = 10         # keep about 0.3 s from before speech is detected
MIN_LOUD_BLOCKS = 8         # need about 0.25 s of actual loud audio to count as speech

audio_queue = queue.Queue()

model_size = "small" #"tiny" #"base" #"small" #"medium" #"large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")


def callback(indata, frames, time_info, status):
    if status:
        print("Status:", status)
    audio_queue.put(indata.copy())


def save_wav(clip, path):
    pcm = (np.clip(clip, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(FS)
        f.writeframes(pcm.tobytes())

def save_transcription(transcription, path):
    with open(path, "w") as f:
        f.write(transcription.strip() + "\n")

def transcribe_clip(clip):
    start = time.perf_counter()
    segments, _ = model.transcribe(clip, beam_size=5, language="en", vad_filter=True)
    segments = list(segments)
    transcription = ""
    
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        transcription += segment.text + " "

    elapsed = time.perf_counter() - start
    print(f"Transcription time: {elapsed:.2f} s")
    return transcription

os.makedirs("clips", exist_ok=True)

preroll = collections.deque(maxlen=PREROLL_BLOCKS)   # last few quiet blocks
utterance = []                                       # blocks of the current command
speaking = False
quiet_count = 0
loud_count = 0
clip_number = 0

print("Listening. Say a command, then pause. Ctrl-C to stop.")
try:
    with sd.InputStream(device=MIC, samplerate=FS, channels=1,
                        dtype="float32", blocksize=BLOCK, callback=callback):
        while True:
            block = audio_queue.get()
            loud = np.sqrt(np.mean(block ** 2)) > THRESHOLD

            if not speaking:
                if loud:
                    speaking = True
                    utterance = list(preroll) + [block]
                    quiet_count = 0
                    loud_count = 1
                    print("speech started")
                else:
                    preroll.append(block)
            else:
                utterance.append(block)
                if loud:
                    loud_count += 1
                    quiet_count = 0
                else:
                    quiet_count += 1
                    if quiet_count >= SILENCE_BLOCKS:
                        clip = np.concatenate(utterance).ravel()
                        if loud_count < MIN_LOUD_BLOCKS:
                            print(f"discarded: too short ({loud_count} loud blocks)")
                        else:
                            clip_number += 1
                            clip_path = f"clips/clip_{clip_number:03d}.wav"
                            transcription_path = f"clips/clip_{clip_number:03d}.txt"
                        
                            transcription = transcribe_clip(clip)

                            save_wav(clip, clip_path)
                            save_transcription(transcription, transcription_path)
                            
                            
                            print(f"speech ended: {len(clip) / FS:.2f} s -> {clip_path} and transcription saved to {transcription_path}")
                        speaking = False
                        preroll.clear()
except KeyboardInterrupt:
    print("Stopped.")