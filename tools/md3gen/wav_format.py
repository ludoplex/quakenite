#!/usr/bin/env python3
"""
WAV file reader/writer for id Tech 3 compatible audio.

Requirements for id Tech 3:
- Mono (1 channel)
- 16-bit PCM
- 22050Hz or 44100Hz sample rate (22050Hz preferred)
"""

import struct
import math
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List


@dataclass
class WAVFile:
    """WAV audio data."""
    sample_rate: int
    samples: List[int]  # 16-bit signed samples (-32768 to 32767)

    @property
    def num_samples(self) -> int:
        return len(self.samples)

    @property
    def duration(self) -> float:
        return self.num_samples / self.sample_rate if self.sample_rate > 0 else 0


def write_wav(wav: WAVFile, filepath: Path):
    """Write a mono 16-bit PCM WAV file."""
    num_channels = 1
    bits_per_sample = 16
    byte_rate = wav.sample_rate * num_channels * bits_per_sample // 8
    block_align = num_channels * bits_per_sample // 8
    data_size = wav.num_samples * block_align

    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + data_size))  # Chunk size
        f.write(b'WAVE')

        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))              # Subchunk size
        f.write(struct.pack('<H', 1))               # Audio format (PCM)
        f.write(struct.pack('<H', num_channels))    # Channels
        f.write(struct.pack('<I', wav.sample_rate)) # Sample rate
        f.write(struct.pack('<I', byte_rate))       # Byte rate
        f.write(struct.pack('<H', block_align))     # Block align
        f.write(struct.pack('<H', bits_per_sample)) # Bits per sample

        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', data_size))

        # Sample data
        for sample in wav.samples:
            # Clamp to 16-bit range
            sample = max(-32768, min(32767, int(sample)))
            f.write(struct.pack('<h', sample))


def read_wav(filepath: Path) -> WAVFile:
    """Read a WAV file (basic PCM only)."""
    with open(filepath, 'rb') as f:
        data = f.read()

    # Verify RIFF header
    if data[0:4] != b'RIFF' or data[8:12] != b'WAVE':
        raise ValueError("Not a valid WAV file")

    # Find fmt chunk
    offset = 12
    sample_rate = 0
    num_channels = 1
    bits_per_sample = 16
    sample_data = b''

    while offset < len(data):
        chunk_id = data[offset:offset + 4]
        chunk_size, = struct.unpack_from('<I', data, offset + 4)

        if chunk_id == b'fmt ':
            audio_format, = struct.unpack_from('<H', data, offset + 8)
            if audio_format != 1:
                raise ValueError(f"Unsupported audio format: {audio_format}")

            num_channels, = struct.unpack_from('<H', data, offset + 10)
            sample_rate, = struct.unpack_from('<I', data, offset + 12)
            bits_per_sample, = struct.unpack_from('<H', data, offset + 22)

        elif chunk_id == b'data':
            sample_data = data[offset + 8:offset + 8 + chunk_size]
            break

        offset += 8 + chunk_size

    # Parse samples
    samples = []
    bytes_per_sample = bits_per_sample // 8 * num_channels

    for i in range(0, len(sample_data), bytes_per_sample):
        if bits_per_sample == 16:
            sample, = struct.unpack_from('<h', sample_data, i)
        else:
            sample = sample_data[i] - 128  # 8-bit is unsigned
            sample *= 256

        # Mix to mono if stereo
        if num_channels == 2 and bits_per_sample == 16:
            sample2, = struct.unpack_from('<h', sample_data, i + 2)
            sample = (sample + sample2) // 2

        samples.append(sample)

    return WAVFile(sample_rate=sample_rate, samples=samples)


# =============================================================================
# Sound Generation Utilities
# =============================================================================

def generate_sine(
    frequency: float,
    duration: float,
    sample_rate: int = 22050,
    amplitude: float = 0.8
) -> WAVFile:
    """Generate a sine wave tone."""
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        sample = math.sin(2 * math.pi * frequency * t) * amplitude * 32767
        samples.append(int(sample))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_noise(
    duration: float,
    sample_rate: int = 22050,
    amplitude: float = 0.5
) -> WAVFile:
    """Generate white noise."""
    num_samples = int(duration * sample_rate)
    samples = [int(random.uniform(-1, 1) * amplitude * 32767) for _ in range(num_samples)]
    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_silence(duration: float, sample_rate: int = 22050) -> WAVFile:
    """Generate silence."""
    num_samples = int(duration * sample_rate)
    return WAVFile(sample_rate=sample_rate, samples=[0] * num_samples)


def apply_envelope(
    wav: WAVFile,
    attack: float,
    decay: float,
    sustain: float,
    release: float
) -> WAVFile:
    """Apply ADSR envelope to audio."""
    sr = wav.sample_rate
    attack_samples = int(attack * sr)
    decay_samples = int(decay * sr)
    release_samples = int(release * sr)
    sustain_samples = max(0, len(wav.samples) - attack_samples - decay_samples - release_samples)

    new_samples = []

    for i, sample in enumerate(wav.samples):
        if i < attack_samples:
            # Attack: 0 to 1
            envelope = i / attack_samples if attack_samples > 0 else 1
        elif i < attack_samples + decay_samples:
            # Decay: 1 to sustain
            progress = (i - attack_samples) / decay_samples if decay_samples > 0 else 1
            envelope = 1 - progress * (1 - sustain)
        elif i < attack_samples + decay_samples + sustain_samples:
            # Sustain
            envelope = sustain
        else:
            # Release: sustain to 0
            remaining = len(wav.samples) - i
            envelope = sustain * (remaining / release_samples) if release_samples > 0 else 0

        new_samples.append(int(sample * envelope))

    return WAVFile(sample_rate=wav.sample_rate, samples=new_samples)


# =============================================================================
# Game Sound Generators
# =============================================================================

def generate_pain_grunt(duration: float = 0.3, pitch: float = 1.0) -> WAVFile:
    """Generate a synthetic pain grunt sound."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    base_freq = 150 * pitch

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Descending pitch
        freq = base_freq * (1.5 - progress * 0.5)

        # Mix of fundamental and harmonics with noise
        signal = (
            math.sin(2 * math.pi * freq * t) * 0.5 +
            math.sin(2 * math.pi * freq * 2 * t) * 0.2 +
            math.sin(2 * math.pi * freq * 3 * t) * 0.1 +
            random.uniform(-1, 1) * 0.2
        )

        # Quick attack, natural decay
        envelope = min(1, i / (0.02 * sample_rate)) * (1 - progress ** 0.5)

        samples.append(int(signal * envelope * 32767 * 0.8))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_death_scream(duration: float = 1.5, pitch: float = 1.0) -> WAVFile:
    """Generate a synthetic death scream sound."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    base_freq = 300 * pitch

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Frequency drops then rises then drops
        freq_mod = 1 + 0.5 * math.sin(progress * math.pi * 2) * (1 - progress)
        freq = base_freq * freq_mod * (1 - progress * 0.3)

        # Complex harmonic content
        signal = (
            math.sin(2 * math.pi * freq * t) * 0.4 +
            math.sin(2 * math.pi * freq * 1.5 * t) * 0.2 +
            math.sin(2 * math.pi * freq * 2 * t) * 0.15 +
            math.sin(2 * math.pi * freq * 3 * t) * 0.1 +
            random.uniform(-1, 1) * 0.15 * (1 - progress)
        )

        # Envelope with sustain
        attack_time = 0.05
        if t < attack_time:
            envelope = t / attack_time
        else:
            envelope = 1 - ((t - attack_time) / (duration - attack_time)) ** 2

        samples.append(int(signal * envelope * 32767 * 0.8))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_jump_sound(duration: float = 0.25, pitch: float = 1.0) -> WAVFile:
    """Generate a jump effort sound."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Rising pitch
        freq = 120 * pitch * (1 + progress * 0.5)

        signal = (
            math.sin(2 * math.pi * freq * t) * 0.5 +
            random.uniform(-1, 1) * 0.3
        )

        envelope = math.sin(progress * math.pi)
        samples.append(int(signal * envelope * 32767 * 0.6))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_build_place_sound(duration: float = 0.2) -> WAVFile:
    """Generate a building placement sound (wooden thunk)."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Low thump with decay
        freq = 80 * (1 - progress * 0.3)

        signal = (
            math.sin(2 * math.pi * freq * t) * 0.6 +
            math.sin(2 * math.pi * freq * 2.5 * t) * 0.2 +
            random.uniform(-1, 1) * 0.3 * (1 - progress)
        )

        # Quick decay
        envelope = (1 - progress) ** 2

        samples.append(int(signal * envelope * 32767 * 0.8))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_build_destroy_sound(duration: float = 0.5) -> WAVFile:
    """Generate a building destruction sound (crash/crumble)."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Noise with low rumble
        freq = 60 * (1 - progress * 0.5)

        signal = (
            math.sin(2 * math.pi * freq * t) * 0.3 +
            random.uniform(-1, 1) * 0.7
        )

        # Decay with initial hit
        if progress < 0.1:
            envelope = progress / 0.1
        else:
            envelope = (1 - (progress - 0.1) / 0.9) ** 1.5

        samples.append(int(signal * envelope * 32767 * 0.8))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_gasp_sound(duration: float = 0.5, pitch: float = 1.0) -> WAVFile:
    """Generate a gasping for air sound."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Breathy noise with slight pitch variation
        freq = 200 * pitch * (1 + 0.2 * math.sin(progress * math.pi * 4))

        signal = (
            random.uniform(-1, 1) * 0.6 +
            math.sin(2 * math.pi * freq * t) * 0.2
        )

        # Quick inhale envelope
        envelope = math.sin(progress * math.pi) ** 0.5

        samples.append(int(signal * envelope * 32767 * 0.5))

    return WAVFile(sample_rate=sample_rate, samples=samples)


def generate_drown_sound(duration: float = 1.5, pitch: float = 1.0) -> WAVFile:
    """Generate a drowning/gurgling sound."""
    sample_rate = 22050
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        progress = i / num_samples

        # Bubbling effect
        bubble_freq = 100 * pitch * (1 + random.uniform(-0.3, 0.3))

        signal = (
            math.sin(2 * math.pi * bubble_freq * t) * 0.3 +
            random.uniform(-1, 1) * 0.4 +
            math.sin(2 * math.pi * 60 * t) * 0.2
        )

        # Modulated envelope for bubbles
        bubble_mod = 0.5 + 0.5 * math.sin(progress * math.pi * 8)
        envelope = (1 - progress ** 2) * bubble_mod

        samples.append(int(signal * envelope * 32767 * 0.6))

    return WAVFile(sample_rate=sample_rate, samples=samples)


if __name__ == "__main__":
    # Generate test sounds
    output_dir = Path("test_sounds")
    output_dir.mkdir(exist_ok=True)

    # Pain grunts
    for level in [25, 50, 75, 100]:
        intensity = level / 100
        wav = generate_pain_grunt(duration=0.3 + intensity * 0.2, pitch=1.0 - intensity * 0.1)
        write_wav(wav, output_dir / f"pain{level}_1.wav")
        print(f"Generated pain{level}_1.wav")

    # Death screams
    for i in range(1, 4):
        wav = generate_death_scream(duration=1.0 + i * 0.3, pitch=1.0 - i * 0.05)
        write_wav(wav, output_dir / f"death{i}.wav")
        print(f"Generated death{i}.wav")

    # Jump
    wav = generate_jump_sound()
    write_wav(wav, output_dir / "jump1.wav")
    print("Generated jump1.wav")

    # Building sounds
    wav = generate_build_place_sound()
    write_wav(wav, output_dir / "build_place.wav")
    print("Generated build_place.wav")

    wav = generate_build_destroy_sound()
    write_wav(wav, output_dir / "build_destroy.wav")
    print("Generated build_destroy.wav")

    # Water sounds
    wav = generate_gasp_sound()
    write_wav(wav, output_dir / "gasp.wav")
    print("Generated gasp.wav")

    wav = generate_drown_sound()
    write_wav(wav, output_dir / "drown.wav")
    print("Generated drown.wav")

    print(f"\nGenerated test WAV files in {output_dir}/")
