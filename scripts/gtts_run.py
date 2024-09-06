from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Generate TTS audio file
tts = gTTS(text='Hello, this is a test. Please do not take this seriously. I will be speaking at different speeds.', lang='en')
tts.save('output.mp3')

# Load the generated audio file using pydub
sound = AudioSegment.from_file('output.mp3')

# Adjust the pitch: Increase by raising the playback speed
new_rate = int(sound.frame_rate * 1.5)  # Adjust the multiplier for different pitch levels
sound_with_pitch = sound._spawn(sound.raw_data, overrides={'frame_rate': new_rate})

# Set the sample rate back to original to play it correctly
sound_with_pitch = sound_with_pitch.set_frame_rate(44100)

# Play the adjusted audio
play(sound_with_pitch)
