import collections
import threading
import time

import numpy as np
from scipy.signal import resample_poly
import sounddevice as sd
from faster_whisper import WhisperModel
import queue

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

FS = 48000                  # 16000 Hz
BLOCK = 512                 # 32 ms
MIC = 10                    # input device number from devices.py (None = system default)
MODEL_SIZE = "small"        # Whisper Model: "tiny" #"base" #"small" #"medium" #"large-v3"

THRESHOLD = 0.008           # between background (0.002) and speech (0.01+)
SILENCE_BLOCKS = 16         # 16 x 32 ms = about 0.5 s of quiet ends a command
PREROLL_BLOCKS = 10         # keep about 0.3 s from before speech is detected
MIN_LOUD_BLOCKS = 8         # need about 0.25 s of actual loud audio to count as speech


class TranscriptionNode:
    def __init__(self):
        super().__init__('transcription_node')
        self.transcription = self.create_publisher(String, '/transcription', 10)
        #Create audio queue for audio collection from stream
        self.audio_queue = queue.Queue()
        #Create voice transcription Faster-Whisper model
        self.model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        #Create Sounddevice InputStream (recording stream)
        self.stream = sd.InputStream(device=MIC, samplerate=FS, channels=1,
                        dtype="float32", blocksize=BLOCK, callback=self.stream_callback)

        self.stop_event = threading.Event()
        self.worker = threading.Thread(target=self.audio_intake)
        self.worker.start() 

    def stop(self):
        self.stop_event.set()        # ask the loop to exit
        self.worker.join()

    def stream_callback(self, indata, status):
        if status:
            print("Status:", status)
            self.audio_queue.put(indata.copy())

    def transcribe(self, clip):
        segments, _ = self.model.transcribe(clip, beam_size=5, language="en", vad_filter=True)
        segments = list(segments)
        transcription = ""
        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text)) #debug only?
            transcription += segment.text + " "
        return transcription
                    
    def audio_intake(self):
        #Init counters, flags for rolling segmentation audio intake
        preroll = collections.deque(maxlen=PREROLL_BLOCKS)   # last few quiet blocks
        utterance = []
        speaking = False 
        quiet_count = 0
        loud_count = 0

        with self.stream:           # stream stays open while the loop runs
            while rclpy.ok() and not self.stop_event.is_set():
                try:
                    block = self.audio_queue.get(timeout=0.1) #adjust timeout length
                except queue.Empty:
                    continue         # nothing yet; re-check the stop flag
                #Process block 
                loud = np.sqrt(np.mean(block ** 2)) > THRESHOLD
                        
                if not speaking:
                    if loud:
                        speaking = True
                        utterance = list(preroll) + [block]
                        quiet_count = 0
                        loud_count = 1
                        #print("speech started")
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
                            clip = resample_poly(clip, 1, FS//16000).astype(np.float32)  # resample to 16 kHz for faster-whisper
                            if loud_count < MIN_LOUD_BLOCKS:
                                #print(f"discarded: too short ({loud_count} loud blocks)")
                                pass
                            else:
                                #clip_number += 1
                                #clip_path = f"clips/clip_{clip_number:03d}.wav"
                                #transcription_path = f"clips/clip_{clip_number:03d}.txt"
                                        
                                transcription = self.transcribe(clip)
                                msg.data = transcription
                                self.transcription.publish(msg)
                                #TODO: fix msg

                                #save_wav(clip, clip_path)
                                #save_transcription(transcription, transcription_path)
                                            
                                            
                                #print(f"speech ended: {len(clip) / FS:.2f} s -> {clip_path} and transcription saved to {transcription_path}")
                            speaking = False
                            preroll.clear()


def main():
    rclpy.init()
    transcription_node = TranscriptionNode()

    try:
        rclpy.spin(transcription_node)

    except KeyboardInterrupt:
        pass

    finally:
        transcription_node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()



if __name__ == '__main__':
    main()




