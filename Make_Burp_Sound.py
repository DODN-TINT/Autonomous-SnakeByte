import numpy as np
import wave
import struct

# Parameters for the sound
sample_rate = 44100         # Samples per second
duration = 0.75              # Duration in seconds (adjust as desired)
n_samples = int(sample_rate * duration)
frequency = 35.0           # Base frequency in Hz (try tweaking this)

# Create a time array for one burst
t = np.linspace(0, duration, n_samples, endpoint=False)

# Create an exponential decay envelope:
# The envelope starts at 1.0 and decays quickly.
envelope = np.exp(-5 * t)

# Create a low-frequency tone
tone = np.sin(2 * np.pi * frequency * t)

# Add a little bit of random noise to give it a "burpy" texture.
# Adjust the noise amplitude (here, 0.2) as needed.
noise = np.random.normal(0, 0.2, size=n_samples)

# Combine tone and noise, then apply the envelope
signal = envelope * (tone + noise)

# Normalize the signal to the range [-1, 1]
max_val = np.max(np.abs(signal))
if max_val > 0:
    signal = signal / max_val

# Convert the signal to 16-bit PCM format.
signal_int16 = np.int16(signal * 32767)

# Write the data to a WAV file
with wave.open("crash.wav", "w") as wf:
    n_channels = 1
    sampwidth = 2  # 2 bytes per sample for 16-bit audio
    wf.setnchannels(n_channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(sample_rate)
    wf.writeframes(signal_int16.tobytes())

print("crash.wav generated successfully!")
