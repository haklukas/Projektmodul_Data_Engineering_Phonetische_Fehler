# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 15:54:05 2019

@author: chkarada
"""
import soundfile as sf
import os
import numpy as np
import librosa

def norm_audio(audio, target_dBFS=-25):
    if len(audio.shape)>1:
        audio = audio.T
        audio = audio.sum(axis=0)/audio.shape[0]
    rms = (audio**2).mean()**0.5
    scalar = 10 ** (target_dBFS / 20) / (rms+1e-6)
    audio = audio * scalar
    return audio

# Function to read audio
def audioread(path, norm = True, start=0, stop=None):
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
    modified_audio = audio * volume_factor
    modified_audio = librosa.effects.time_stretch(modified_audio, rate=speed_factor)
    return modified_audio

def add_interruptions(audio, sampling_rate, interruption_length=0.5, num_interruptions=1):
    
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
