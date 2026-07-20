# -*- coding: utf-8 -*-
"""
This module provides small utility functions for reading, writing and manipulating audio.

Created on Wed Jun 26 15:54:05 2019
@author: chkarada
"""
import soundfile as sf
import os
import numpy as np
import librosa
from audiotsm import wsola
from audiotsm.io.array import ArrayReader, ArrayWriter
from scipy.signal import resample_poly



def norm_audio(audio, target_dBFS=-25):
    """
    Normalize an audio signal to a target dBFS level.

    Args:
        audio (np.ndarray): Audio samples.
        target_dBFS (float): Desired dBFS level (default: -25).

    Returns:
        np.ndarray: Normalized audio samples.
    """

    if len(audio.shape)>1:
        audio = audio.T
        audio = audio.sum(axis=0)/audio.shape[0]
    rms = (audio**2).mean()**0.5
    scalar = 10 ** (target_dBFS / 20) / (rms+1e-6)
    audio = audio * scalar
    return audio

# Function to read audio
def audioread(path, norm = True, start=0, stop=None):
    """
    Read an audio file from disk and optionally normalize it.

    Args:
        path (str): Path to audio file.
        norm (bool): If True, normalize the audio (default: True).
        start (int|None): Optional start frame for partial reads.
        stop (int|None): Optional stop frame for partial reads.

    Returns:
        (np.ndarray, int): Tuple containing the audio and its samplerate.
    """

    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise ValueError("[{}] does not exist!".format(path))
    try:
        x, sr = sf.read(path, start=start, stop=stop)
    except RuntimeError:  # fix for sph pcm-embedded shortened v2
        print('WARNING: Audio type not supported')

    if norm:
        x = norm_audio(x)
    return x, sr    
    
# Funtion to write audio    
def audiowrite(data, fs, destpath, norm=False):
    """
    Write audio data to disk, optionally normalizing first.

    Args:
        data (np.ndarray): Audio samples.
        fs (int): Sample rate in Hz.
        destpath (str): Destination file path.
        norm (bool): If True, normalize before writing (default: False).

    Returns:
        None
    """

    if norm:
        data = norm_audio(data)
    
    destpath = os.path.abspath(destpath)
    destdir = os.path.dirname(destpath)
    
    if not os.path.exists(destdir):
        os.makedirs(destdir)
    
    sf.write(destpath, data, fs)
    return

# Function to mix clean speech and noise at various SNR levels
def snr_mixer(clean, noise, snr):
    """
    Mix clean speech and noise to produce a noisy signal at a target SNR.

    Args:
        clean (np.ndarray): Clean speech samples.
        noise (np.ndarray): Noise samples.
        snr (float): Desired SNR in dB.

    Returns:
        (np.ndarray, np.ndarray, np.ndarray): Tuple containing the clean signal, processed noise and noisy signal.
    """

    # Normalizing to -25 dB FS
    rmsclean = (clean**2).mean()**0.5
    scalarclean = 10 ** (-25 / 20) / rmsclean
    clean = clean * scalarclean
    rmsclean = (clean**2).mean()**0.5

    rmsnoise = (noise**2).mean()**0.5
    scalarnoise = 10 ** (-25 / 20) /rmsnoise
    noise = noise * scalarnoise
    rmsnoise = (noise**2).mean()**0.5
    
    # Set the noise level for a given SNR
    noisescalar = np.sqrt(rmsclean / (10**(snr/20)) / rmsnoise)
    noisenewlevel = noise * noisescalar
    noisyspeech = clean + noisenewlevel
    return clean, noisenewlevel, noisyspeech
        
def modify_audio(audio, volume_factor=1.0, speed_factor=1.0):
    """
    Apply volume and speed changes to an audio signal.

    Args:
        audio (np.ndarray): Audio samples.
        volume_factor (float): Volume multiplier.
        speed_factor (float): Speed multiplier.

    Returns:
        np.ndarray: Modified audio samples.
    """

    modified_audio = audio * volume_factor

    reader = ArrayReader(modified_audio.reshape(1, -1))
    writer = ArrayWriter(channels=reader.channels)

    tsm = wsola(reader.channels, speed=speed_factor)
    tsm.run(reader, writer)
    modified_audio = writer.data.flatten()
    #modified_audio = librosa.effects.time_stretch(modified_audio, rate=speed_factor)
    return modified_audio

def add_interruptions(audio, sampling_rate, interruption_length=0.5, num_interruptions=1):
    """
    Insert silent interruptions into the audio at random positions.

    Args:
        audio (np.ndarray): Audio samples.
        sampling_rate (int): Samplerate in Hz.
        interruption_length (float): Length of each interruption in seconds.
        num_interruptions (int): Number of interruptions to insert.

    Returns:
        np.ndarray: Audio with interruptions inserted.
    """

    modified_audio = audio.copy()
    interruption_samples = int(interruption_length * sampling_rate)
    for _ in range(num_interruptions):
        start = np.random.randint(0, len(audio) - interruption_samples)
        max_attempts = 20
        while np.any(modified_audio[start:start + interruption_samples] == 0) and max_attempts > 0:
            start = np.random.randint(0, len(audio) - interruption_samples)
            max_attempts -= 1
        modified_audio[start:start + interruption_samples] = 0
    return modified_audio

def match_samplerate(audio, sr_in, sr_target):
    # Upsample/downsample using rational factor
    gcd = np.gcd(sr_in, sr_target)
    up = sr_target // gcd
    down = sr_in // gcd
    return resample_poly(audio, up, down)
