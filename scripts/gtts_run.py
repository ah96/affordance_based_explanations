#!/usr/bin/env python3
"""
Speech demo with Google Text-to-Speech (gTTS), without ROS.

Converts a text to speech with the ``gtts`` package, raises the pitch with
``pydub`` and plays the result.  The pitch is raised by playing the samples
at a higher frame rate, which also shortens the audio.

Dependencies
------------
    pip install gtts pydub
    pydub needs ffmpeg or libav on the system.

Usage
-----
    python3 gtts_run.py
    Speaks the demo sentence below.  Replace ``text`` with an explanation.
"""

from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Text to synthesize.  Replace it with a textual explanation of verbalize.py.
text = (
    'Hello, this is a test. '
    'Please do not take this seriously. '
    'I will be speaking at different speeds.'
)

# Step 1: generate TTS audio via the Google API and save to a temporary file.
tts = gTTS(text=text, lang='en')
tts.save('output.mp3')

# Step 2: load the MP3 with pydub for post-processing.
sound = AudioSegment.from_file('output.mp3')

# Step 3: raise pitch by increasing the frame rate (multiplier > 1 = higher pitch).
# Adjust the multiplier (currently 1.5) to taste; 1.0 = no change.
pitch_multiplier = 1.5
new_rate = int(sound.frame_rate * pitch_multiplier)
sound_high = sound._spawn(sound.raw_data, overrides={'frame_rate': new_rate})

# Step 4: reset frame rate to standard 44 100 Hz before playback.
sound_high = sound_high.set_frame_rate(44100)

# Step 5: play the pitch-adjusted audio.
play(sound_high)
