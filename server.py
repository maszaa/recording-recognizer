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
      configuration.ARCCLOUD_CONFIGURATION
    )
    return recognizer.record_and_recognize()

  return app
