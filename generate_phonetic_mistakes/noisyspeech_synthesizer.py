"""
@author: chkarada
"""
import glob
import shutil
import numpy as np
import os
from audiolib import norm_audio, audioread, audiowrite, snr_mixer, match_samplerate
import librosa

def synthesize_noisy_speech(audios=None, orig_sr=16000, snr_lower=0.0, snr_upper=40.0, total_snrlevels=5, clean_dir=None, noise_dir=None, sampling_rate=16000, audioformat='*.wav', silence_length=0.2, write_processed_files=True, noisyspeech_dir=None, clean_proc_dir=None, noise_proc_dir=None, noise_types_excluded=None):
    """
    Description:
        Generate noisy speech examples by mixing clean speech with environmental noise
        at various SNR levels. Can read from disk or accept in-memory audio arrays.

    Args:
        audios: Optional list of clean numpy audio arrays to use instead of reading them from clean_dir.
        orig_sr: Original sampling rate of input audio waveforms in Hz (default: 16000).
        snr_lower: Lower bound for SNR in dB (default: 0 dB).
        snr_upper: Upper bound for SNR in dB (default: 40 dB).
        total_snrlevels: Number of SNR levels to generate between lower and upper bound. Includes the bounds themselves (default: 5).
        clean_dir: Directory containing clean speech files (if audios is None) (default: None, which looks at 'clean').
        noise_dir: Directory containing noise audio files (default: None, which looks at 'noise').
        sampling_rate: Output sampling rate in Hz (default: 16000).
        audioformat: File format for audio files (default: '*.wav').
        silence_length: Duration of silence in s introduced during noise transitions occuring if a noise file is shorter than the audio (default: 0.2).
        write_processed_files: If True, write processed clean/noisy/noise files to disk. (default: True)
        noisyspeech_dir: Output directory for noisy speech files. (default: None, which creates 'NoisySpeech_After')
        clean_proc_dir: Output directory for processed clean speech files (default: None, which creates 'CleanSpeech_After').
        noise_proc_dir: Output directory for processed noise files(default: None, which creates 'Noise_After').
        noise_types_excluded: Optional list of filename prefixes to exclude from noise pool, for example: noise_types_excluded= ["Babble", "AirConditioner"] (default: None).

    Returns:
        (list, list, list): Tuple containing lists of the noisy speech, clean speech and processed noise
    """

    print("Starting synthesis of noisy speech dataset...")

    if audios is None:
        if clean_dir is None:
            clean_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "clean"))
        if not os.path.exists(clean_dir):
            assert False, ("Clean speech data is required")
    
    if noise_dir is None:
        noise_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "noise"))
    if not os.path.exists(noise_dir):
        assert False, ("Noise data is required")
        
    fs = float(sampling_rate)
    if write_processed_files:
        if noisyspeech_dir is None:
            noisyspeech_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "NoisySpeech_After"))
        if os.path.exists(noisyspeech_dir):
            shutil.rmtree(noisyspeech_dir)
        os.makedirs(noisyspeech_dir)
        if clean_proc_dir is None:     
            clean_proc_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "CleanSpeech_After"))
        if os.path.exists(clean_proc_dir):
            shutil.rmtree(clean_proc_dir)
        os.makedirs(clean_proc_dir)
        if noise_proc_dir is None:
            noise_proc_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "Noise_After"))
        if os.path.exists(noise_proc_dir):
            shutil.rmtree(noise_proc_dir)
        os.makedirs(noise_proc_dir)
        
    SNR = np.linspace(snr_lower, snr_upper, total_snrlevels)
    if audios is None:
        cleanfilenames = glob.glob(os.path.join(clean_dir, audioformat))
    if noise_types_excluded is None:
        noisefilenames = glob.glob(os.path.join(noise_dir, audioformat))
    else:
        noisefilenames = glob.glob(os.path.join(noise_dir, audioformat))
        for i in range(len(noise_types_excluded)):
            noisefilenames = [fn for fn in noisefilenames if not os.path.basename(fn).startswith(noise_types_excluded[i])]
    
    filecounter = 0
    num_samples = 0
    if audios is None:
        num_wavs = np.size(cleanfilenames)
    else:
        num_wavs = len(audios)

    noisy_speech = []
    clean_speech = []
    noise_proc = []

    for idx_s in range(num_wavs):
        if audios is None:
            clean, orig_sr = audioread(cleanfilenames[idx_s])
        else:
            clean = norm_audio(audios[idx_s])

        if orig_sr != sampling_rate:
            clean = match_samplerate(clean, orig_sr, sampling_rate)

        idx_n = np.random.randint(0, np.size(noisefilenames))
        noise, fs = audioread(noisefilenames[idx_n])
        
        if len(noise)>=len(clean):
            noise = noise[0:len(clean)]
        
        else:
        
            while len(noise)<=len(clean):
                idx_n = idx_n + 1
                if idx_n >= np.size(noisefilenames)-1:
                    idx_n = np.random.randint(0, np.size(noisefilenames))
                newnoise, fs = audioread(noisefilenames[idx_n])
                noiseconcat = np.append(noise, np.zeros(int(fs*silence_length)))
                noise = np.append(noiseconcat, newnoise)
        noise = noise[0:len(clean)]
        filecounter = filecounter + 1
        
        for i in range(np.size(SNR)):
            clean_snr, noise_snr, noisy_snr = snr_mixer(clean=clean, noise=noise, snr=SNR[i])
            if write_processed_files:
                noisyfilename = 'noisy'+str(filecounter)+'_SNRdb_'+str(SNR[i])+'_clnsp'+str(filecounter)+'.wav'
                cleanfilename = 'clnsp'+str(filecounter)+'.wav'
                noisefilename = 'noise'+str(filecounter)+'_SNRdb_'+str(SNR[i])+'.wav'
                noisypath = os.path.join(noisyspeech_dir, noisyfilename)
                cleanpath = os.path.join(clean_proc_dir, cleanfilename)
                noisepath = os.path.join(noise_proc_dir, noisefilename)
                audiowrite(noisy_snr, fs, noisypath, norm=False)
                audiowrite(clean_snr, fs, cleanpath, norm=False)
                audiowrite(noise_snr, fs, noisepath, norm=False)
            noisy_speech.append(noisy_snr)
            clean_speech.append(clean_snr)
            noise_proc.append(noise_snr)
            num_samples = num_samples + len(noisy_snr)
            print("Generated file {} with SNR {} dB. Noisy files generated: {} of {}".format(i, SNR[i], (filecounter-1) * total_snrlevels + i + 1, num_wavs * total_snrlevels))
        
    return noisy_speech, clean_speech, noise_proc
            
    