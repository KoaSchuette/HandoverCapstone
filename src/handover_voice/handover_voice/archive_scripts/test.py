""" import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

audio = sd.rec(
    int(10 * 16000),
    samplerate=16000,
    channels=1,
    dtype="float32"
)

sd.wait()

print("Recording successful!")
print("Audio shape:", audio.shape)
print("Peak amplitude:", np.max(np.abs(audio)))
write("test_recording_1.wav", 16000, audio) """

#voice live
from faster_whisper import WhisperModel
import sounddevice as sd
import time
from datetime import datetime

print("Execution time:", datetime.now())
#= set-up
model_size = "small" #"tiny" #"small"
print("Using faster-whisper model:", model_size)
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# print(sd.query_devices())

#= Recording
duration = 15 #seconds
fs = 16000 #44100 and 48000 is standard according to SD. faster-whisper processes at 16k default

print("Starting Recording, start speaking in 1s")
time.sleep(1)
print("Now")
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1) #returns array float 32 default.

sd.wait()
print("Finished Recording")

#= Processing


segments, info = model.transcribe(myrecording.flatten(), beam_size=5, language="en", word_timestamps=True) #beam size 5 might be overkill, trying 3. uses 16000 freq
segments = list(segments)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

words = [
    word
    for segment in segments
    for word in segment.words
]

for previous, current in zip(words, words[1:]):
    pause = current.start - previous.end
    print(f"{previous.word} → {current.word}: {pause:.3f} s")