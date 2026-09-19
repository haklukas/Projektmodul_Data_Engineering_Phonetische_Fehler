import whisper
import numpy as np
from pathlib import Path


def _load_whisper_model(model_name):
    model_url = whisper._MODELS.get(model_name)
    if model_url is not None:
        model_path = Path.home() / ".cache" / "whisper" / Path(model_url).name
        if model_path.is_file():
            return whisper.load_model(str(model_path), device="cpu")

    return whisper.load_model(model_name, device="cpu")

def stt (audios, language=None,stt_name="Whisper_turbo"):
    if stt_name == "Whisper_turbo":
        return stt_whisper(audios, language=language, model="turbo")
    elif stt_name == "Whisper_tiny":
        return stt_whisper(audios, language=language, model="tiny")
    elif stt_name == "Whisper_tiny_en":
        return stt_whisper(audios, language=language, model="tiny.en")
    elif stt_name == "Whisper_base":
        return stt_whisper(audios, language=language, model="base")
    elif stt_name == "Whisper_base_en":
        return stt_whisper(audios, language=language, model="base.en")
    elif stt_name == "Whisper_small":
        return stt_whisper(audios, language=language, model="small")
    elif stt_name == "Whisper_small_en":
        return stt_whisper(audios, language=language, model="small.en")
    elif stt_name == "Whisper_medium":
        return stt_whisper(audios, language=language, model="medium")
    elif stt_name == "Whisper_medium_en":
        return stt_whisper(audios, language=language, model="medium.en")
    else:
        raise Exception(f"No STT of name {stt_name} supported.")

def stt_whisper(audios, language=None, model="turbo" ):
    """
    Description:
        Perform speech-to-text transcription using Whisper.

    Args:
        audios: A filename, numpy array, or list of such audio inputs.
        language: Optional language hint for transcription.

    Returns:
        list of transcribed strings corresponding to each audio input.
    """

    model = _load_whisper_model(model)
    texts = []
    if isinstance(audios, str) or isinstance(audios, np.ndarray):
        audios = [audios]
    step = 0
    for audio in audios:
        step += 1
        print(f"Transcribing audio {step} of {len(audios)}")
        if isinstance(audio, np.ndarray):
            audio = audio.astype(np.float32)
        if language is not None:
            result = model.transcribe(audio, language=language)
        else:
            result = model.transcribe(audio)
        texts.append(result["text"])
    return texts