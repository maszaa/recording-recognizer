import time

ARCCLOUD_CONFIGURATION = {}
ACRCLOUD_RESULT_SCORE_THRESHOLD = 95

SAMPLE_RATE = 48000
DURATION = 30
CHANNELS = 1

AUDIO_FILEPATH = "/tmp"
AUDIO_FORMAT = "wav"

NOISE_AUDIO_FILEPATH = None

HIGH_PASS_FREQUENCY = 100
HIGH_PASS_ORDER = 30/6 # 30 dB / octave

def GET_AUDIO_FILENAME():
  return f"{AUDIO_FILEPATH}/{time.time_ns()}.{AUDIO_FORMAT}"

try:
  from local_configuration import *
except ModuleNotFoundError:
  pass
