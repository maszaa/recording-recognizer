import datetime
import json
import os
import pprint
import traceback

import sounddevice

from acrcloud.recognizer import ACRCloudRecognizer
from pydub import AudioSegment, effects
from scipy.io import wavfile

class AudioRecognizer:
  def __init__(self, sample_rate, duration, channels, filename, audio_format, acrcloud_config, recognizer_start_offset=0):
    self.sample_rate = sample_rate
    self.duration = duration
    self.channels = channels
    self.filename = filename
    self.audio_format = audio_format
    self.recognizer = ACRCloudRecognizer(acrcloud_config)
    self.recognizer_start_offset = recognizer_start_offset

  def _log_action(self, action, ready=False):
    print(f"[{datetime.datetime.now()}] {self.filename}: {action} - {'ready' if ready else 'started'}")

  def record(self):
    self._log_action(self.record.__name__)
    recording = sounddevice.rec(
      int(self.duration * self.sample_rate),
      samplerate=self.sample_rate,
      channels=self.channels
    )
    sounddevice.wait()
    wavfile.write(self.filename, self.sample_rate, recording)
    self._log_action(self.record.__name__, ready=True)

  def normalize(self):
    self._log_action(self.normalize.__name__)
    raw_sound = AudioSegment.from_file(self.filename, self.audio_format)
    normalized_sound = effects.normalize(raw_sound)
    normalized_sound.export(self.filename, format=self.audio_format)
    self._log_action(self.normalize.__name__, ready=True)

  def delete_recording(self):
    self._log_action(self.delete_recording.__name__)
    os.remove(self.filename)
    self._log_action(self.delete_recording.__name__, ready=True)

  def recognize(self):
    self._log_action(self.recognize.__name__)
    result = json.loads(
      self.recognizer.recognize_by_file(
        self.filename,
        self.recognizer_start_offset
      )
    )
    pprint.pprint(result)

    metadata = result.get("metadata", {}).get("music", [{}])[0]

    if "metadata" in result:
      del result["metadata"]

    self._log_action(self.recognize.__name__, ready=True)

    return {
      "artist": metadata.get("artists", [{}])[0].get("name"),
      "album": metadata.get("album", {}).get("name"),
      "title": metadata.get("title"),
      "__info": result
    }

  def record_and_recognize(self):
    self._log_action(self.record_and_recognize.__name__)
    result = {}

    try:
      self.record()
      self.normalize()
      result = self.recognize()
      self.delete_recording()
    except Exception as e:
      traceback.print_exc()
      result = {
        "error": str(e)
      }

    self._log_action(self.record_and_recognize.__name__, ready=True)
    return result
