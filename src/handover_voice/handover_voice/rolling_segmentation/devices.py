import sounddevice as sd

def device_query():
    print(sd.query_devices())
    print("Default (input,output):", sd.default.device)

device_query()