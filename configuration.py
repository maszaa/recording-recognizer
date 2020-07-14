from datetime import datetime

ARCCLOUD_CONFIGURATION = {}

SAMPLE_RATE = 48000
DURATION = 30
CHANNELS = 1

AUDIO_FILEPATH = "/tmp"
AUDIO_FORMAT = "wav"

def GET_AUDIO_FILENAME():
  return f"{AUDIO_FILEPATH}/{datetime.now().microsecond}"

try:
  from local_configuration import *
except ModuleNotFoundError:
  pass
