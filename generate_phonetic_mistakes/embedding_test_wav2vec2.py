import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import numpy as np
from scipy.spatial.distance import cosine

processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
model.eval()

def load_audio(path):
    waveform, sr = torchaudio.load(path)
    if sr != 16000:
        resampler = torchaudio.transforms.Resample(sr, 16000)
        waveform = resampler(waveform)
    return waveform.squeeze()  # remove channel dimension

def extract_embedding(audio_tensor):
    # Prepare input for wav2vec2
    inputs = processor(audio_tensor, sampling_rate=16000, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(inputs.input_values)
    
    # Hidden states shape: (batch, time, features)
    hidden_states = outputs.last_hidden_state.squeeze(0)

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
print(f"Cosine similarity: {sim:.4f}")
