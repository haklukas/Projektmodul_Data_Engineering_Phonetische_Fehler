import torch
import torchaudio
import numpy as np
from scipy.spatial.distance import cosine
from transformers import WhisperProcessor, WhisperModel

processor = WhisperProcessor.from_pretrained("openai/whisper-base")
model = WhisperModel.from_pretrained("openai/whisper-base")
model.eval()

def load_audio(path):
    audio, sr = torchaudio.load(path)
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        audio = resampler(audio)
    return audio.squeeze()  # mono

def extract_embedding(audio_tensor):
    # Whisper expects log-mel spectrograms, not raw audio
    inputs = processor(audio_tensor, sampling_rate=16000, return_tensors="pt")

    with torch.no_grad():
        # Use ONLY the encoder
        encoder_outputs = model.encoder(inputs.input_features)

    # Hidden states: (batch, time, features)
    hidden_states = encoder_outputs.last_hidden_state.squeeze(0)

    # Mean pooling over time → fixed-length vector
    embedding = hidden_states.mean(dim=0)

    return embedding.numpy()


def compare_audios(file1, file2):
    audio1 = load_audio(file1)
    audio2 = load_audio(file2)

    emb1 = extract_embedding(audio1)
    emb2 = extract_embedding(audio2)

    similarity = 1 - cosine(emb1, emb2)
    return similarity


file_clean = "modified_audio_11.wav"
file_noisy = "eval_11.wav"

sim = compare_audios(file_clean, file_noisy)
print(f"Whisper embedding similarity: {sim:.4f}")

