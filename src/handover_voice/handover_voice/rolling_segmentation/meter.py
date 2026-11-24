import queue
import numpy as np
import sounddevice as sd
import time

FS = 16000
BLOCK = 512         # 512 samples = 32 ms per block
MIC = None          # same number as before

audio_queue = queue.Queue()

def callback(indata, frames, time_info, status):
    # Runs on a background thread every 32 ms
    if status:
        print("Status:", status)
    audio_queue.put(indata.copy())  # Copy: the buffer is reused

print("Listening. Press Ctrl-C to stop.")
try:
    with sd.InputStream(device=MIC, samplerate=FS, channels=1,
                        dtype="float32", blocksize=BLOCK,
                        callback=callback):
        while True:
            block = audio_queue.get()                # waits for the next block
            rms = np.sqrt(np.mean(block ** 2))       # loudness of this block
            # print(f"{rms:.4f} " + "#" * int(rms * 300))
            time.sleep(0.1)   # pretend our processing is slow
            print(f"queue size: {audio_queue.qsize()}")
except KeyboardInterrupt:
    print("Stopped.")