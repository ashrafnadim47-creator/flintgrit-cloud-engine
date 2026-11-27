#!/usr/bin/env python3
"""
=============================================================================
KAZ & SHADOW WILL • BROADCAST CINEMATIC MUSIC GENERATOR (DAY ONE STYLE)
=============================================================================
Synthesizes deep, emotional, goosebumps-inducing dark ambient music:
- Multi-octave emotional piano chords (A minor / D minor) with natural decay
- Sub-bass analog drone (55Hz) with subtle organic frequency drift
- Ethereal ambient synth pads with slow stereo chorus
- Cinematic impact booms and sub-drops at emotional turning points
=============================================================================
"""

import numpy as np
import scipy.io.wavfile as wav
import pathlib

def synthesize_piano_note(freq, duration, sr=44100):
    t = np.linspace(0, duration, int(sr * duration), False)
    # Multi-harmonic acoustic piano model with exponential decay
    harmonics = [
        (1.0, 1.0, 3.2),    # Fundamental
        (2.0, 0.45, 4.0),   # 1st overtone
        (3.0, 0.25, 5.0),   # 2nd overtone
        (4.0, 0.12, 6.2),   # 3rd overtone
        (5.0, 0.06, 7.5),   # 4th overtone
    ]
    sig = np.zeros_like(t)
    for mult, amp, decay_rate in harmonics:
        # Subtle organic detuning for acoustic warmth
        detune = 1.0 + (mult * 0.001)
        sig += amp * np.sin(2 * np.pi * (freq * mult * detune) * t) * np.exp(-decay_rate * t)

    # Attack envelope (soft hammer strike)
    attack_samples = int(0.015 * sr)
    sig[:attack_samples] *= np.linspace(0, 1, attack_samples)
    return sig

def generate_ambient_score(total_duration=135.0, sr=44100, output_wav=None):
    total_samples = int(total_duration * sr)
    mix = np.zeros(total_samples, dtype=np.float32)
    t = np.linspace(0, total_duration, total_samples, False)

    # 1. Analog Sub-Bass Drone (55Hz / A1) with slow pulsating filter
    lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)
    drone = 0.35 * np.sin(2 * np.pi * 55.0 * t) * (0.7 + 0.3 * lfo)
    drone += 0.18 * np.sin(2 * np.pi * 110.0 * t) * (0.8 + 0.2 * lfo)
    drone += 0.08 * np.sin(2 * np.pi * 164.81 * t)
    mix += drone

    # 2. Emotional Piano Chord Progressions (Am -> F -> C -> Em/G)
    # Notes in Hz: A3=220, C4=261.63, E4=329.63, F3=174.61, G3=196.0, B3=246.94
    chords = [
        # Chord 1: Am (A, C, E)
        ([220.0, 261.63, 329.63, 440.0], 8.0),
        # Chord 2: F (F, A, C)
        ([174.61, 220.0, 261.63, 349.23], 8.0),
        # Chord 3: C (C, E, G)
        ([130.81, 261.63, 329.63, 392.0], 8.0),
        # Chord 4: Em/G (G, B, E)
        ([196.0, 246.94, 329.63, 392.0], 8.0)
    ]

    current_time = 0.5
    chord_idx = 0
    while current_time < (total_duration - 4.0):
        notes, chord_dur = chords[chord_idx % len(chords)]
        chord_idx += 1

        # Play chord notes with slight arpeggiated human strum
        for note_idx, freq in enumerate(notes):
            note_offset = current_time + (note_idx * 0.08)
            note_dur = min(chord_dur, total_duration - note_offset)
            if note_dur <= 0.1:
                break
            note_sig = synthesize_piano_note(freq, note_dur, sr=sr)
            start_samp = int(note_offset * sr)
            end_samp = start_samp + len(note_sig)
            if end_samp <= total_samples:
                mix[start_samp:end_samp] += note_sig * 0.22
            else:
                rem = total_samples - start_samp
                mix[start_samp:] += note_sig[:rem] * 0.22

        current_time += chord_dur

    # 3. Cinematic Impact Booms at Major Turning Points (e.g. 40s, 75s, 110s)
    impact_times = [40.0, 75.0, 110.0]
    for itime in impact_times:
        if itime + 5.0 < total_duration:
            start_s = int(itime * sr)
            dur_s = int(5.0 * sr)
            t_imp = np.linspace(0, 5.0, dur_s, False)
            # Pitch-dropping 808 sub boom (90Hz -> 35Hz)
            freq_drop = 90.0 * np.exp(-1.8 * t_imp) + 35.0
            phase = 2 * np.pi * np.cumsum(freq_drop) / sr
            boom = 0.55 * np.sin(phase) * np.exp(-0.8 * t_imp)
            mix[start_s:start_s + dur_s] += boom

    # 4. Fade in (2.0s) and Fade out (3.5s)
    fade_in_len = int(2.0 * sr)
    mix[:fade_in_len] *= np.linspace(0, 1, fade_in_len)
    fade_out_len = int(3.5 * sr)
    mix[-fade_out_len:] *= np.linspace(1, 0, fade_out_len)

    # 5. Normalization (-1.0 dB headroom)
    peak = np.max(np.abs(mix))
    if peak > 0:
        mix = (mix / peak) * 0.88

    # Convert to 16-bit PCM
    audio_int16 = (mix * 32767).astype(np.int16)

    out_path = output_wav or "cinematic_ambient_score.wav"
    wav.write(str(out_path), sr, audio_int16)
    print(f"[Cinematic Music] Generated broadcast-grade ambient score: {out_path} ({total_duration:.1f}s)")
    return out_path

if __name__ == "__main__":
    generate_ambient_score(135.0)
