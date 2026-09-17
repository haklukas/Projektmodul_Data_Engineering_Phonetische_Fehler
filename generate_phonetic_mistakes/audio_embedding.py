from functools import lru_cache

import torch
from scipy.spatial.distance import cosine
from transformers import (
    WhisperModel,
    WhisperProcessor,
    Wav2Vec2Model,
    Wav2Vec2Processor,
)


TARGET_SAMPLE_RATE = 16000


@lru_cache(maxsize=2)
def load_model(embedding):
    if embedding == "whisper":
        processor = WhisperProcessor.from_pretrained("openai/whisper-base")
        model = WhisperModel.from_pretrained("openai/whisper-base")
    elif embedding == "wav2vec2":
        processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
        model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")
    else:
        raise ValueError("embedding must be 'whisper' or 'wav2vec2'")

    model.eval()
    return processor, model


def prepare_audio(audio):
    waveform = torch.as_tensor(audio, dtype=torch.float32)
    if waveform.ndim == 2:
        waveform = waveform.mean(dim=0) if waveform.shape[0] <= 2 else waveform.mean(dim=1)
    if waveform.ndim != 1:
        raise ValueError("audio must be a one-dimensional waveform")

    return waveform


def extract_whisper_embedding(audio):
    processor, model = load_model("whisper")
    waveform = prepare_audio(audio)
    inputs = processor(
        waveform.numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    with torch.no_grad():
        hidden_states = model.encoder(inputs.input_features).last_hidden_state

    return hidden_states.squeeze(0).mean(dim=0).cpu().numpy()


def extract_wav2vec2_embedding(audio):
    processor, model = load_model("wav2vec2")
    waveform = prepare_audio(audio)
    inputs = processor(
        waveform.numpy(),
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt",
    )

    with torch.no_grad():
        hidden_states = model(inputs.input_values).last_hidden_state

    return hidden_states.squeeze(0).mean(dim=0).cpu().numpy()


def cosine_similarity(embedding1, embedding2):
    return 1 - cosine(embedding1, embedding2)


def compare_whisper(audio1, audio2):
    embedding1 = extract_whisper_embedding(audio1)
    embedding2 = extract_whisper_embedding(audio2)
    return cosine_similarity(embedding1, embedding2)


def compare_wav2vec2(audio1, audio2):
    embedding1 = extract_wav2vec2_embedding(audio1)
    embedding2 = extract_wav2vec2_embedding(audio2)
    return cosine_similarity(embedding1, embedding2)


def compare_audio_embeddings(audio1, audio2, embedding="whisper"):
    """Return cosine similarity between two 16 kHz in-memory waveforms."""
    if embedding == "whisper":
        return compare_whisper(audio1, audio2)
    elif embedding == "wav2vec2":
        return compare_wav2vec2(audio1, audio2)
    else:
        raise ValueError("No audio embedding named '{}' supported.".format(embedding))