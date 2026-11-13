#oct 25th, 26th
from faster_whisper import WhisperModel
import sounddevice as sd
import time
from datetime import datetime
import numpy as np
import queue

print("Execution time:", datetime.now())
#= set-up
model_size = "small" #"tiny" #"base" #"small" #"medium" #"large-v3"
fs = 16000 #44100 and 48000 is standard according to SD. faster-whisper processes at 16k default
sd.default.device = 1 #Microphone (Arctis Nova 7), MME (3 in, 0 out)
audio_queue = queue.Queue()

print("Using faster-whisper model:", model_size)
model = WhisperModel(model_size, device="cpu", compute_type="int8")

#= Recording
myrec = []
sample_count = 0
loop_flag = True

# Recording Callback
def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

print("Enter Stream")

# Recording Stream + Loop
with sd.InputStream(channels=1, samplerate=fs, callback=callback):
    while loop_flag:
        audio = audio_queue.get()
        
        myrec.append(audio)
        sample_count += audio.shape[0]

        if sample_count >= (5*fs): #80,000 frames
            clip = np.concatenate(myrec, axis=0).ravel() #.flatten()
            # print("Audio shape:", clip.shape)
            print("Audio duration:", len(clip) / fs)

            start = time.perf_counter()

            segments, _ = model.transcribe(clip, beam_size=5, language="en")
            segments = list(segments)

            elapsed = time.perf_counter() - start
            print(f"Transcription took {elapsed:.2f} seconds")

            for segment in segments:
                print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
                if "exit sequence" in segment.text.lower():
                    loop_flag = False

            myrec = []
            sample_count = 0


print("Exit Stream time:", datetime.now())


print("Finished.")

