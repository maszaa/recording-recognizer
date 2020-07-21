from flask import Flask

from audio_recognizer import AudioRecognizer

import configuration

def get_app():
  app = Flask(__name__)

  @app.route('/recognize')
  def recognize():
    recognizer = AudioRecognizer(
      configuration.SAMPLE_RATE,
      configuration.DURATION,
      configuration.CHANNELS,
      configuration.GET_AUDIO_FILENAME(),
      configuration.AUDIO_FORMAT,
      configuration.HIGH_PASS_FREQUENCY,
      configuration.HIGH_PASS_ORDER,
      configuration.ARCCLOUD_CONFIGURATION,
      noise_audio_filepath=configuration.NOISE_AUDIO_FILEPATH
    )
    return recognizer.record_and_recognize()

  return app
