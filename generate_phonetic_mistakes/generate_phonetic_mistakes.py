
from pathlib import Path
import soundfile as sf
import numpy as np
import random
from audiolib import modify_audio, add_interruptions, audioread, audiowrite, match_samplerate
from audio_embedding import compare_audio_embeddings
from noisyspeech_synthesizer import *
import Levenshtein
import phonetics
import cologne_phonetics
import textdistance
import spellwise
import jellyfish
import re
from num2words import num2words
import string
from textclass_params import Textclasses, PARAMS
from tts import tts_single
from stt import stt

def evaluate_phonetic_mistake(clean_audio, text, noisy_text, language, voice, tts_name="Piper", clean_audio_sr=16000, audio_id=0, save_audio=False):

    # eliminate punctuation and convert numbers to words
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    if language == "english":
        text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group())), text)
    elif language == "german":
        text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group()), lang= "de"), text)
        
    text = text.translate(translator)
    text = text.strip()

    noisy_text = noisy_text.translate(translator)
    if language == "english":
        noisy_text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group())), noisy_text)
    elif language == "german":
        noisy_text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group()), lang= "de"), noisy_text)

    noisy_text = noisy_text.translate(translator)
    noisy_text = noisy_text.strip()

    # eliminate candidates that are exactly the same as the original text
    if not noisy_text or noisy_text == text:
        if not noisy_text:
            print(f"Skipping evaluation {audio_id}: noisy transcription is empty after normalization.")
        return -1

    # get audio from the noisy text using the same voice and TTS configuration
    if isinstance(voice, tuple):
        voice_configuration = [(voice[0], None if voice[1] is None else [voice[1]])]
    else:
        voice_configuration = voice
    noisy_audio_data, noisy_audio_sr = tts_single(noisy_text, voice_configuration, tts_name)
    noisy_audio = noisy_audio_data[0][0]

    audio_tests_dir = Path("Audio_Tests")
    audio_tests_dir.mkdir(parents=True, exist_ok=True)
    if save_audio:
        clean_audio_path = audio_tests_dir / f"clean_audio_{audio_id}.wav"
        noisy_audio_path = audio_tests_dir / f"noisy_audio_{audio_id}.wav"
        audiowrite(clean_audio, clean_audio_sr, clean_audio_path)
        audiowrite(noisy_audio, noisy_audio_sr, noisy_audio_path)

        print("--------------------------------------------------")
        print(f"Phonetic evaluation {audio_id}")
        print(f"Original text: {text}")
        print(f"Noisy text: {noisy_text}")
        print(f"Language: {language}")
        print(f"Voice: {voice}")
        print(f"TTS: {tts_name}")
        print(f"Clean audio: {clean_audio_path}")
        print(f"Noisy audio: {noisy_audio_path}")
        print(f"Clean sample rate: {clean_audio_sr}")
        print(f"Noisy sample rate: {noisy_audio_sr}")

    #create audio embeddings for the clean and noisy audio and get the cosine similarity
    clean_audio_16k = match_samplerate(clean_audio, clean_audio_sr, 16000)
    noisy_audio_16k = match_samplerate(noisy_audio, noisy_audio_sr, 16000)
    eval = compare_audio_embeddings(clean_audio_16k, noisy_audio_16k, embedding="whisper")

    if save_audio:
        print(f"Whisper cosine similarity: {eval}")

    return eval

'''def evaluate_phonetic_mistakes(text, noisy_text, language):
    """
    """Description:
        Evaluate phonetic and edit-distance differences between original and noisy transcriptions.

    Args:
        text: Original reference text.
        noisy_text: Noisy or transcribed text to compare.
        language: Language identifier (e.g., "german", "english").

    Returns:
        dict of metrics
    """

    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    if language == "english":
        text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group())), text)
    elif language == "german":
        text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group()), lang= "de"), text)
    
    noisy_text = noisy_text.translate(translator)
    if language == "english":
        noisy_text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group())), noisy_text)
    elif language == "german":
        noisy_text = re.sub(r"[0-9]+", lambda m: num2words(int(m.group()), lang= "de"), noisy_text)

    eval = dict()

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
    eval["levenshtein"] = levenshtein_dist

    
    jaro_winkler = Levenshtein.jaro_winkler(text, noisy_text)
    jaro_winkler_dist = 1 - jaro_winkler
    print(f"Jaro Winkler similiarity to original: {jaro_winkler}, distance: {jaro_winkler_dist}")
    print("------------------")
    eval["jaro_winkler"] = jaro_winkler_dist

    damerau = textdistance.DamerauLevenshtein().distance(text, noisy_text)
    print(f"Damerau-Levenshtein distance to original: {damerau}")
    print("------------------")
    eval["damerau"] = damerau

    monge_elkan_orig_left = textdistance.MongeElkan().distance(text, noisy_text)
    print(f"Monge-Elkan distance to original with original left: {monge_elkan_orig_left}")
    print("------------------")
    eval["monge_elkan_orig_left"] = monge_elkan_orig_left

    monge_elkan_orig_right = textdistance.MongeElkan().distance(noisy_text, text)
    print(f"Monge-Elkan distance to original with original right: {monge_elkan_orig_right}")
    print("------------------")
    eval["monge_elkan_orig_right"] = monge_elkan_orig_right

    lcsstr = textdistance.LCSStr().distance(text, noisy_text)
    print(f"Longest common substring distance with original: {lcsstr}")
    print("------------------")
    eval["lcsstr"] = lcsstr

    caver1 = spellwise.CaverphoneOne()
    caver1.add_words([text])
    caver1_dist = caver1.get_suggestions(noisy_text, max_distance=500)[0]["distance"]
    print(f"CaverphoneOne distance to original: {caver1_dist}")
    print("------------------")
    eval["caverphoneOne"] = caver1_dist

    caver2 = spellwise.CaverphoneTwo()
    caver2.add_words([text])
    caver2_dist = caver2.get_suggestions(noisy_text, max_distance=500)[0]["distance"]
    print(f"CaverphoneTwo distance to original: {caver2_dist}")
    print("------------------")
    eval["caverphoneTwo"] = caver2_dist

    nysiis_text = jellyfish.nysiis(text)
    print(f"Original text encoded by nysiis: {nysiis_text}")
    nysiis_noisy_text = jellyfish.nysiis(noisy_text)
    print(f"Noisy text encoded by nysiis: {nysiis_noisy_text}")
    print("------------------")
    eval["nysiis"] = (nysiis_text, nysiis_noisy_text)
    
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
    
    return eval'''

"""def normalize_metrics(metrics_list):
    norm_metrics_list = []
    min_metrics = dict()
    max_metrics = dict()
    for metrics in metrics_list:
        norm_metrics = dict()
        for metric_name, metric_value in metrics.items():
            if metric_name == "dmetaphone":
                lev_dists = []
                lev_dists.append(Levenshtein.distance(metric_value[0][0], metric_value[1][0]))
                if metric_value[1][1] != "":
                    lev_dists.append(Levenshtein.distance(metric_value[0][0], metric_value[1][1]))
                if metric_value[0][1] != "":
                    lev_dists.append(Levenshtein.distance(metric_value[0][1], metric_value[1][0]))
                    if metric_value[1][1] != "":
                        lev_dists.append(Levenshtein.distance(metric_value[0][1], metric_value[1][1]))
                norm_metrics[metric_name] = min(lev_dists)
            elif isinstance(metric_value, tuple):
                norm_metrics[metric_name] = Levenshtein.distance(metric_value[0], metric_value[1])
            else:
                norm_metrics[metric_name] = metric_value
            if metric_name not in min_metrics or norm_metrics[metric_name] < min_metrics[metric_name]:
                min_metrics[metric_name] = norm_metrics[metric_name]
            if metric_name not in max_metrics or norm_metrics[metric_name] > max_metrics[metric_name]:
                            max_metrics[metric_name] = norm_metrics[metric_name]
        norm_metrics_list.append(norm_metrics)

    print(f"Min metrics: {min_metrics}")
    print(f"Max metrics: {max_metrics}")

    for metrics in norm_metrics_list:
        for metric_name in metrics.keys():
            metrics[metric_name] = (metrics[metric_name] - min_metrics[metric_name]) / (max_metrics[metric_name] - min_metrics[metric_name])

    print(norm_metrics_list)

    return norm_metrics_list"""

"""def pick_mistake(text, noisy_texts, language, severity):
    metrics_list = []
    noisy_texts = [noisy_text for noisy_text in noisy_texts if noisy_text != text]
    for noisy_text in noisy_texts:
        metrics = evaluate_phonetic_mistakes(text, noisy_text, language)
        metrics_list.append(metrics)
    metrics_list = normalize_metrics(metrics_list)
    combo_metric_list = [(noisy_texts[i], sum(metrics_list[i].values()) / len(metrics_list[i].values())) for i in range(len(noisy_texts))]
    print(f"CML: {combo_metric_list}")
    combo_metric_list.sort(key= lambda combo_metric : combo_metric[1])
    print(f"CML2: {combo_metric_list}")
    split_list = np.array_split(np.array(combo_metric_list, dtype=np.dtype('U500, float')), 10)
    print(f"Split list: {split_list}")
    candidates = list(split_list[severity-1])
    print(f"Candidates: {candidates}")
    if candidates == []:
        mistake = combo_metric_list[-1]
    else:
        mistake = random.choice(candidates)
    print(mistake)
    return mistake[0]"""

"""def is_similar_sounding(text, noisy_text, language):

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

    return is_similar_sounding"""


def generate_phonetic_mistakes(text, textclass, text_language, stt_language, voices, tts_name="Piper", stt_name="Whisper_turbo", return_filenames=False):
    """Description:
        Synthesize audio, apply transformations and noise layers, run STT, and evaluate phonetic mistakes.

    Args:
        text: Input text to synthesize.
        textclass: Textclasses enum indicating the text category.
        text_language: Language of the input text.
        stt_language: Language hint for the STT engine.
        voices: Voices configuration for synthesis.
        severity: desired severity of mistakes. From 1 to 10.
        tts_name: TTS engine selection (default: "Piper").
        stt_name: STT engine selection (default: "Whisper").

    Returns:
        None (prints evaluation results).
    """

    if isinstance(textclass, Textclasses): 
        params = PARAMS[textclass]
    else:
        params = textclass
    audio_data, orig_sr = tts_single(text=text, voices=voices, tts_name=tts_name)
    audios = [data[0] for data in audio_data]
    audio_metadata = [data[1] for data in audio_data]

    modified_audios = []
    modified_audio_metadata = []
    modified_audio_sources = []
    for i in range(len(audios)):
        audio = audios[i]
        for vol in params["volumes"]:
            for spd in params["speeds"]:
                modified_audio = modify_audio(audio, volume_factor=vol, speed_factor=spd)
                modified_audios.append(modified_audio)
                modified_audio_metadata.append(audio_metadata[i])
                modified_audio_sources.append((audio, orig_sr, audio_metadata[i]))
                if params["num_interrupts"] > 0:
                    modified_audio_interrupted = add_interruptions(modified_audio, orig_sr, interruption_length=params["len_interrupts"], num_interruptions=params["num_interrupts"])
                    modified_audios.append(modified_audio_interrupted)
                    modified_audio_metadata.append(audio_metadata[i])
                    modified_audio_sources.append((audio, orig_sr, audio_metadata[i]))

    for i in range(len(modified_audios)):
        audiowrite(modified_audios[i], orig_sr, os.path.join("clean", f"modified_audio_{i}.wav"))

    print(f"Number of modified audio versions: {len(modified_audios)}")
    print(f"Number of modified audio metadata entries: {len(modified_audio_metadata)}")
    audios = modified_audios

    noisy_speech_metadata = []
    noisy_speech_sources = []
    print(f"orig_sr: {orig_sr}")
    if params["noise_layers"] > 0:
            
        noisy_speech_all = []
        noisy_speech_all_sources = []
        noisy_speech_all_filenames = []
        step = 0
        sr = 16000
        for i in range(params["noise_layers"]):
            step += 1
            layer_output_dir = os.path.join("NoisySpeech_After", f"layer_{step}")
            if step == 1:
                synthesis_result = synthesize_noisy_speech(audios = audios, orig_sr=orig_sr, snr_lower=params["snr_lower"], snr_upper=params["snr_upper"], total_snrlevels=params["total_snrlevels"], write_processed_files = True, sampling_rate=sr, noisyspeech_dir=layer_output_dir, return_filenames=return_filenames)
            else:
                synthesis_result = synthesize_noisy_speech(audios = audios, orig_sr=sr, snr_lower=params["snr_lower"], snr_upper=params["snr_upper"], total_snrlevels=params["total_snrlevels"], write_processed_files = True, sampling_rate=sr, noisyspeech_dir=layer_output_dir, return_filenames=return_filenames)
            if return_filenames:
                noisy_speech, clean_speech, noise, layer_filenames = synthesis_result
                noisy_speech_all_filenames.extend(layer_filenames)
            else:
                noisy_speech, clean_speech, noise = synthesis_result
            noisy_speech_all.extend(noisy_speech)
            print("##########################################")
            print(f"Number of new noisy speech versions after layer {step}: {len(audios)}")
            noisy_versions_per_clean_audio = len(noisy_speech) // len(audios)
            print(f"Number of noisy versions per clean audio: {noisy_versions_per_clean_audio}")
            print(len(noisy_speech) / len(audios))
            layer_metadata = [md for md in modified_audio_metadata for _ in range(noisy_versions_per_clean_audio)]
            layer_sources = [source for source in modified_audio_sources for _ in range(noisy_versions_per_clean_audio)]
            noisy_speech_metadata.extend(layer_metadata)
            noisy_speech_sources = layer_sources
            noisy_speech_all_sources.extend(layer_sources)
            print(len(noisy_speech_metadata))
            print("##########################################")
            audios = noisy_speech.copy()
            modified_audio_metadata = noisy_speech_metadata.copy()
            modified_audio_sources = noisy_speech_sources.copy()
        
        noisy_texts = stt(noisy_speech_all, language=stt_language, stt_name=stt_name)
        noisy_speech_sources = noisy_speech_all_sources

    else:
        noisy_texts = stt(audios, language=stt_language, stt_name=stt_name)
        noisy_speech_sources = modified_audio_sources
        noisy_speech_all_filenames = [None] * len(noisy_texts)

    evaluation_results = []
    voice_audio_counts = {}
    voice_ids = {}
    for i, noisy_text in enumerate(noisy_texts):
        clean_audio, clean_audio_sr, voice = noisy_speech_sources[i]
        voice_key = repr(voice)
        if voice_key not in voice_ids:
            voice_ids[voice_key] = len(voice_ids)
        voice_audio_id = voice_audio_counts.get(voice_key, 0)
        voice_audio_counts[voice_key] = voice_audio_id + 1
        evaluation_results.append(
            (noisy_text,
             noisy_speech_all_filenames[i] if return_filenames else None,
                evaluate_phonetic_mistake(
                    clean_audio=clean_audio,
                    text=text,
                    noisy_text=noisy_text,
                    language=text_language,
                    voice=voice,
                    tts_name=tts_name,
                    clean_audio_sr=clean_audio_sr,
                    audio_id=f"voice_{voice_ids[voice_key]}_audio_{voice_audio_id}",
                )
            )
        )

    """
    evalspeech_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "EvalSpeech"))

    if os.path.exists(evalspeech_dir):
        shutil.rmtree(evalspeech_dir)
    os.makedirs(evalspeech_dir)

    for i in range(len(noisy_texts)):
        noisy_text = noisy_texts[i]
        metadata = noisy_speech_metadata[i]
        print(f"Noisy text: {noisy_text}")
        voice_pack_path, speaker_id = metadata
        evalspeech_data, eval_sr = tts_single(text=noisy_text, voices=[(voice_pack_path, [speaker_id])], tts_name=tts_name)
        eval_audio = evalspeech_data[0][0]
        audiowrite(eval_audio, eval_sr, os.path.join(evalspeech_dir, f"eval_{i}.wav"))
    """

    """
    mistake = pick_mistake(text, noisy_texts, text_language, severity)
    similar_sounding_texts = []
    for noisy_text in noisy_texts:
        if is_similar_sounding(text=text, noisy_text=noisy_text, language=text_language):
            similar_sounding_texts.append(noisy_text)

    print(noisy_texts)"""

    evaluation_results = [result for result in evaluation_results if result[2] != -1]
    print(f"Number of valid evaluation results: {len(evaluation_results)}")
    # sort evaluation results by similarity score descending (higher similarity means more similar sounding)
    evaluation_results.sort(key=lambda x: x[2], reverse=True)
    print(f"Sorted evaluation results: {evaluation_results}")

    if return_filenames:
        return [(result[0], result[1]) for result in evaluation_results]
    return [result[0] for result in evaluation_results]

def get_phonetic_mistake_single(text, textclass, text_language, stt_language, voices, severity, tts_name="Piper", stt_name="Whisper_turbo", return_filename=False):
    results = generate_phonetic_mistakes(text=text, textclass=textclass, text_language=text_language, stt_language=stt_language, voices=voices, tts_name=tts_name, stt_name=stt_name, return_filenames=return_filename)
    if len(results) == 0:
        print("No valid evaluation results found.")
        return None
    # choose the result corresponding to the desired severity level (1-10)
    # The results are divided into 10 equal parts and a random result is selected from the part corresponding to the severity level.
    split_results = np.array_split(np.array(results), 10)
    selected_results = split_results[severity - 1] if severity <= len(split_results) else split_results[-1]
    selected_result = random.choice(selected_results)
    print(f"Selected result for severity {severity}: {selected_result}")
    return selected_result

def get_phonetic_mistake_block(text, textclass, text_language, stt_language, voices, severity, tts_name="Piper", stt_name="Whisper_turbo"):
    results = generate_phonetic_mistakes(text=text, textclass=textclass, text_language=text_language, stt_language=stt_language, voices=voices, tts_name=tts_name, stt_name=stt_name)
    if len(results) == 0:
        print("No valid evaluation results found.")
        return None
    # choose the result corresponding to the desired severity level (1-10)
    # The results are divided into 10 equal parts and a random result is selected from the part corresponding to the severity level.
    split_results = np.array_split(np.array(results), 10)
    selected_results = split_results[severity - 1] if severity <= len(split_results) else split_results[-1]
    print(f"Selected results for severity {severity}: {selected_results}")
    return selected_results