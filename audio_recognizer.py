import datetime
import json
import os
import pprint
import traceback

import noisereduce
import numpy
import pydub.scipy_effects
import sounddevice

from acrcloud.recognizer import ACRCloudRecognizer
from pydub import AudioSegment, effects
from scipy.io import wavfile

class AudioRecognizer:
  def __init__(
    self,
    sample_rate,
    duration,
    channels,
    filename,
    audio_format,
    high_pass_frequency,
    high_pass_order,
    acrcloud_config,
    acrcloud_result_score_threshold,
    recognizer_start_offset=0,
    noise_audio_filepath=None,
    additional_operations=None
  ):
    self.sample_rate = sample_rate
    self.duration = duration
    self.channels = channels
    self.filename = filename
    self.audio_format = audio_format
    self.high_pass_frequency = high_pass_frequency
    self.high_pass_order = high_pass_order
    self.recognizer = ACRCloudRecognizer(acrcloud_config)
    self.acrcloud_result_score_threshold = acrcloud_result_score_threshold
    self.recognizer_start_offset = recognizer_start_offset
    self.noise_audio_filepath = noise_audio_filepath

    if not additional_operations:
      additional_operations = []
    self.additional_operations = additional_operations

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

  def high_pass_filter(self):
    self._log_action(self.high_pass_filter.__name__)
    raw_sound = AudioSegment.from_file(self.filename, self.audio_format)
    high_passed_sound = raw_sound.high_pass_filter(
      self.high_pass_frequency,
      order=self.high_pass_order
    )
    high_passed_sound.export(self.filename, format=self.audio_format)
    self._log_action(self.high_pass_filter.__name__, ready=True)

  def denoise(self):
    if self.noise_audio_filepath:
      self._log_action(self.denoise.__name__)
      fs, original_sound = wavfile.read(self.filename)
      fs, noisy_sound = wavfile.read(self.noise_audio_filepath)
      denoised_sound = noisereduce.reduce_noise(
        audio_clip=original_sound,
        noise_clip=noisy_sound
      )
      wavfile.write(self.filename, self.sample_rate, numpy.asarray(denoised_sound, dtype=numpy.float32))
      self._log_action(self.denoise.__name__, ready=True)

  def delete_recording(self):
    self._log_action(self.delete_recording.__name__)
    os.remove(self.filename)
    self._log_action(self.delete_recording.__name__, ready=True)

  def recognize(self):
    self._log_action(self.recognize.__name__)
    result = json.loads(
      self.recognizer.recognize_by_file(
        self.filename,
        self.recognizer_start_offset,
        rec_length=self.duration
      )
    )
    pprint.pprint(result)

    metadata = result.get("metadata", {}).get("music", [{}])[0]

    if metadata.get("score", 0) < self.acrcloud_result_score_threshold:
      metadata = {}
    else:
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
      self.denoise()
      self.high_pass_filter()
      self.normalize()
      result = self.recognize()

      for additional_operation in self.additional_operations:
        additional_operation(self, result)

      self.delete_recording()
    except Exception as e:
      traceback.print_exc()
      result = {
        "error": str(e)
      }

    self._log_action(self.record_and_recognize.__name__, ready=True)
    return result
