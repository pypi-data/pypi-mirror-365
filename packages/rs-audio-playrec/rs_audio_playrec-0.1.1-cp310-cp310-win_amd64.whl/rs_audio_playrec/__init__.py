"""
High-performance audio playback and recording library for Python.

This library provides fast, low-latency audio playback and recording capabilities
with support for multiple formats (WAV, AIF, MP3) and high-quality audio processing.
"""

from ._rs_audio_playrec import (
    Player,
    Recorder,
    load_audio_file,
    save_audio_file,
    get_audio_info,
    list_output_devices,
    list_input_devices,
    convert_audio,
)

__version__ = "0.1.0"
__author__ = "hiroshi-tamura"

__all__ = [
    "Player",
    "Recorder", 
    "load_audio_file",
    "save_audio_file",
    "get_audio_info",
    "list_output_devices",
    "list_input_devices",
    "convert_audio",
    "play_file",
    "record_to_file",
    "AudioPlayer",
    "AudioRecorder",
    "AudioData",
]

# Convenience aliases
AudioPlayer = Player
AudioRecorder = Recorder

# Create AudioData class for compatibility
class AudioData:
    """Audio data container."""
    def __init__(self, samples, channels, sample_rate, bit_depth):
        self.samples = samples
        self.channels = channels
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth

def play_file(path, device=None, volume=1.0, loop=False):
    """
    Quick function to play an audio file.
    
    Args:
        path (str): Path to the audio file
        device (str, optional): Output device name
        volume (float): Volume level (0.0 to 2.0)
        loop (bool): Whether to loop the audio
    
    Returns:
        Player: Player instance for control
    """
    if device:
        player = Player.with_device(device)
    else:
        player = Player()
    player.load(path)
    player.set_volume(volume)
    player.set_loop(loop)
    player.play()
    return player

def record_to_file(path, duration=None, device=None, sample_rate=44100, channels=2):
    """
    Quick function to record audio to a file.
    
    Args:
        path (str): Output file path
        duration (float, optional): Recording duration in seconds
        device (str, optional): Input device name
        sample_rate (int): Sample rate in Hz
        channels (int): Number of channels
    
    Returns:
        Recorder: Recorder instance for control
    """
    if device:
        recorder = Recorder.with_device(device)
    else:
        recorder = Recorder()
    recorder.set_format(sample_rate, channels)
    recorder.start()
    
    if duration:
        import time
        time.sleep(duration)
        recorder.stop()
        recorder.save(path)
    
    return recorder

# Sample rate constants
SAMPLE_RATE_22050 = 22050
SAMPLE_RATE_24000 = 24000
SAMPLE_RATE_32000 = 32000
SAMPLE_RATE_44100 = 44100
SAMPLE_RATE_48000 = 48000
SAMPLE_RATE_88200 = 88200
SAMPLE_RATE_96000 = 96000
SAMPLE_RATE_192000 = 192000

# Bit depth constants
BIT_DEPTH_8 = 8
BIT_DEPTH_16 = 16
BIT_DEPTH_24 = 24
BIT_DEPTH_32 = 32
BIT_DEPTH_64 = 64