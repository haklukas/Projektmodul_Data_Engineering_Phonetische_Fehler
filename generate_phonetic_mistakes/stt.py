import whisper
import numpy as np

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

    model = whisper.load_model(model, device="cpu")
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