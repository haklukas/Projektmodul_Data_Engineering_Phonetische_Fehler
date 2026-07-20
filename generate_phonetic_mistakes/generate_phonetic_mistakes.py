
from pathlib import Path
import soundfile as sf
import numpy as np
from audiolib import modify_audio, add_interruptions, audioread, audiowrite
from noisyspeech_synthesizer import *
import Levenshtein
import phonetics
import cologne_phonetics
import re
from num2words import num2words
import string
from textclass_params import Textclasses, PARAMS
from tts import tts_single
from stt import stt

def evaluate_phonetic_mistakes(text, noisy_text, language):
    """
    Description:
        Evaluate phonetic and edit-distance differences between original and noisy transcriptions.

    Args:
        text: Original reference text.
        noisy_text: Noisy or transcribed text to compare.
        language: Language identifier (e.g., "german", "english").

    Returns:
        None (prints evaluation summary to stdout).
    """
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    if language == "english":
        text = re.sub(r"\d+", lambda m: num2words(int(m.group())), str.replace(text, ))
    elif language == "german":
        text = re.sub(r"\d+", lambda m: num2words(int(m.group()), lang= "de"), text)
    
    noisy_text = noisy_text.translate(translator)
    if language == "english":
        noisy_text = re.sub(r"\d+", lambda m: num2words(int(m.group())), noisy_text)
    elif language == "german":
        noisy_text = re.sub(r"\d+", lambda m: num2words(int(m.group()), lang= "de"), noisy_text)

    print("--------------------------------------------------")
    print("Evaluation:")
    print(f"Original text: {text}")
    print(f"Transcription for Noisy version: {noisy_text}")
    print("------------------")

    levenshtein_dist = Levenshtein.distance(text, noisy_text)
    levenshtein_ratio = Levenshtein.ratio(text, noisy_text)
    print(f"Levenshtein distance to original: {levenshtein_dist}, ratio: {levenshtein_ratio}")
    levenshtein_req_edits = Levenshtein.editops(text, noisy_text)
    print(f"Required Edits: {levenshtein_req_edits}")
    print("------------------")

    eval = dict()

    if language == "german":
        print("Cologne Phonetics:")
        cph_text = cologne_phonetics.encode(text)
        encoded_text = ""
        for _, encoded_substr in cph_text:
            encoded_text += encoded_substr 
        print(f"Original text encoded by Cologne Phonetics: {encoded_text}")
        cph_noisy_text = cologne_phonetics.encode(noisy_text)
        encoded_noisy_text = ""
        for _, encoded_substr in cph_noisy_text:
            encoded_noisy_text += encoded_substr
        eval["cologne_phonetics"] = (encoded_text, encoded_noisy_text)
        print(f"Noisy text encoded by Cologne Phonetics: {encoded_noisy_text}")
        print("------------------")

    if language == "english":
        print("Soundex:")
        sanitized_text = re.sub('[^a-z]', '', str(text).lower())
        sanitized_noisy = re.sub('[^a-z]', '', str(noisy_text).lower())
        soundex_text = phonetics.soundex(sanitized_text) if sanitized_text else ''
        print(f"Original text encoded by Soundex: {soundex_text}")
        soundex_noisy_text = phonetics.soundex(sanitized_noisy) if sanitized_noisy else ''
        eval["soundex"] = (soundex_text, soundex_noisy_text)
        print(f"Noisy text encoded by Soundex: {soundex_noisy_text}")
        print("------------------")

    print("Metaphone:")
    metaphone_text = phonetics.metaphone(str(text).lower())
    print(f"Original text encoded by Metaphone: {metaphone_text}")
    metaphone_noisy_text = phonetics.metaphone(str(noisy_text).lower())
    eval["metaphone"] = (metaphone_text, metaphone_noisy_text)
    print(f"Noisy text encoded by Metaphone: {metaphone_noisy_text}")
    print("------------------")

    print("Double Metaphone:")
    dmetaphone_text = phonetics.dmetaphone(str(text).lower())
    print(f"Original text encoded by Double Metaphone: {dmetaphone_text}")
    dmetaphone_noisy_text = phonetics.dmetaphone(str(noisy_text).lower())
    eval["dmetaphone"] = (dmetaphone_text, dmetaphone_noisy_text)
    print(f"Noisy text encoded by Double Metaphone: {dmetaphone_noisy_text}")
    print("--------------------------------------------------")

    return eval

def is_similar_sounding(text, noisy_text, language):

    eval = evaluate_phonetic_mistakes(text, noisy_text, language)

    is_similar_sounding = False
    for algo, values in eval.items():
        if algo == "dmetaphone":
            if len([x for x in values[0] if x in values[1] and x != '']) > 0:
                is_similar_sounding = True
                print("####################################################")
                print(f"{text} is similar to {noisy_text} by algorithm {algo} : {values[0]} and {values[1]} have overlap")
                print("####################################################")
        elif values[0] == values[1]:
            is_similar_sounding = True
            print("####################################################")
            print(f"{text} is similar to {noisy_text} by algorithm {algo} : {values[0]} = {values[1]}")
            print("####################################################")

    return is_similar_sounding




def generate_phonetic_mistakes(text, textclass, text_language, stt_language, voices, tts_name="Piper", stt_name="Whisper_turbo"):
    """
    Description:
        Synthesize audio, apply transformations and noise layers, run STT, and evaluate phonetic mistakes.

    Args:
        text: Input text to synthesize.
        textclass: Textclasses enum indicating the text category.
        text_language: Language of the input text.
        stt_language: Language hint for the STT engine.
        voices: Voices configuration for synthesis.
        tts: TTS engine selection (default: "Piper").

    Returns:
        None (prints evaluation results).
    """

    if isinstance(textclass, Textclasses): 
        params = PARAMS[textclass]
    else:
        params = textclass
    audio_data, orig_sr = tts_single(text=text, voices=voices, tts_name=tts_name)
    audios = [data[0] for data in audio_data]

    modified_audios = []
    for audio in audios:
        for vol in params["volumes"]:
            for spd in params["speeds"]:
                modified_audio = modify_audio(audio, volume_factor=vol, speed_factor=spd)
                modified_audios.append(modified_audio)
                if params["num_interrupts"] > 0:
                    modified_audio_interrupted = add_interruptions(modified_audio, orig_sr, interruption_length=params["len_interrupts"], num_interruptions=params["num_interrupts"])
                    modified_audios.append(modified_audio_interrupted)
                    
    for i in range(len(modified_audios)):
        audiowrite(modified_audios[i], orig_sr, os.path.join("clean", f"modified_audio_{i}.wav"))

    print(f"Number of modified audio versions: {len(modified_audios)}")
    audios = modified_audios

    print(f"orig_sr: {orig_sr}")
    if params["noise_layers"] > 0:
            
        noisy_speech_all = []
        step = 0
        sr = 16000
        for i in range(params["noise_layers"]):
            step += 1
            if step == 1:
                noisy_speech, clean_speech, noise = synthesize_noisy_speech(audios = audios, orig_sr=orig_sr, snr_lower=params["snr_lower"], snr_upper=params["snr_upper"], total_snrlevels=params["total_snrlevels"], write_processed_files = True, sampling_rate=sr)
            else:
                noisy_speech, clean_speech, noise = synthesize_noisy_speech(audios = audios, orig_sr=sr, snr_lower=params["snr_lower"], snr_upper=params["snr_upper"], total_snrlevels=params["total_snrlevels"], write_processed_files = True, sampling_rate=sr)
            noisy_speech_all.extend(noisy_speech)
            audios = noisy_speech
        
        noisy_texts = stt(noisy_speech_all, language=stt_language, stt_name=stt_name)

    else:
        noisy_texts = stt(audios, language=stt_language, stt_name=stt_name)

    similar_sounding_texts = []
    for noisy_text in noisy_texts:
        if is_similar_sounding(text=text, noisy_text=noisy_text, language=text_language):
            similar_sounding_texts.append(noisy_text)

    print(noisy_texts)
    return similar_sounding_texts
