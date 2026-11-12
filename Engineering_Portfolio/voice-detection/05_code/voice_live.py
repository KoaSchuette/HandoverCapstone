#oct 19th
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
sd.default.device = 1 #Microphone (Arctis Nova 7), MME (3 in, 0 out)

print("Starting Recording, start speaking in 1s")
time.sleep(1)
print("Now")
myrecording = sd.rec(int(duration * fs), samplerate=fs, channels=1) #returns array float 32 default.

sd.wait()
print("Finished Recording")

#= Processing


segments, info = model.transcribe(myrecording.flatten(), beam_size=5, language="en") #beam size 5 might be overkill, trying 3. uses 16000 freq
segments = list(segments)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))