import wave
from piper import PiperVoice, SynthesisConfig
import io
import soundfile as sf
from audiolib import match_samplerate

    
def tts_single(text, voices, tts_name="Piper"):
    if tts_name == "Piper":
        return tts_piper_single(text, voices)
    else:
        raise Exception(f"No TTS of name {tts_name} supported.")

def tts_piper_single(text, voices):

    """
    Description:
        Text-to-speech synthesis for a single text input using Piper.

    Args:
        text (string): A single text to be transformed to speech
        voices: List of (voice_pack_path, speaker_ids) tuples. speaker_ids are None when the voice pack doesnt have multiple speakers.

    Returns:
        (wavs_data, samplerate) ((list, int)): A tuple containing wavs_data and samplerate where wavs_data is a list of
            (wav_array, (voice_pack_path, speaker_id)) tuples.
    """

    wavs_data = []
    samplerate = -1

    for voice_pack, speaker_ids in voices:
        voice = PiperVoice.load(voice_pack)

        if speaker_ids is None or len(speaker_ids) == 0:
            syn_config = SynthesisConfig(
                volume=1,
                length_scale=1,
                noise_scale=1.0,
                noise_w_scale=1.0,
                normalize_audio=True,
            )
            buffer = io.BytesIO()

            with wave.open(buffer, "wb") as wav_file:
                voice.synthesize_wav(text, wav_file, syn_config=syn_config)

            wav_bytes = buffer.getvalue()

            wav, new_samplerate = sf.read(io.BytesIO(wav_bytes))
            if new_samplerate != samplerate:
                if samplerate == -1:
                    samplerate = new_samplerate
                else:
                    wav = match_samplerate(wav, new_samplerate, samplerate)

            wav_data = (wav, (voice_pack, None))
            wavs_data.append(wav_data)

        else:
            for speaker_id in speaker_ids:
                syn_config = SynthesisConfig(
                    speaker_id=speaker_id,
                    volume=1,
                    length_scale=1,
                    noise_scale=1.0,
                    noise_w_scale=1.0,
                    normalize_audio=True,
                )

                buffer = io.BytesIO()

                with wave.open(buffer, "wb") as wav_file:
                    voice.synthesize_wav(text, wav_file, syn_config=syn_config)

                wav_bytes = buffer.getvalue()
                wav, new_samplerate = sf.read(io.BytesIO(wav_bytes))
                if new_samplerate != samplerate:
                    if samplerate == -1:
                        samplerate = new_samplerate
                    else:
                        wav = match_samplerate(wav, new_samplerate, samplerate)
                
                wav_data = (wav, (voice_pack, speaker_id))
                wavs_data.append(wav_data)

    return wavs_data, samplerate

