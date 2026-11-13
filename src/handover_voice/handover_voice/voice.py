from faster_whisper import WhisperModel

model_size = "small"

model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe(r"C:\Users\mrrya\Documents\MREN403\misc\recordings\word_list_Oct14_22_41.mp3", beam_size=5)
segments = list(segments)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))