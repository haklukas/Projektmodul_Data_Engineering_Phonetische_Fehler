from pathlib import Path
import os
from textclass_params import Textclasses, PARAMS
from generate_phonetic_mistakes import generate_phonetic_mistakes

SKIP_STT = False
TEST_CASE  = True
ONLY_TEST = True
SYNTHESIZE_NOISE = True

TO_MEMORY = False

LAYERS_NOISE = 2
#VOLUMES = [0.5, 1.0, 2.0]
VOLUMES = [1.0]
#SPEEDS = [0.5, 1.0, 1.5]
SPEEDS = [1.0]
NUM_INTERRUPTS = 3
LEN_INTERRUPTS = 0.2

if __name__ == "__main__":

    #text = "Bosnien und Herzegowina"
    #text = "L'arc de Triomphe"
    #text = "Samsung"
    text = "17543"
    #text = "siebzehntausendfünfhundertfünfundfünfzig"
    #text = "ein heißer Mittwochabend mit vielen Eiswürfeln"

    #text = "Maria Sklodowska-Curie"
    #text = "seventeen thousand five hundred and fifty five"
    #textclass = Textclasses.NAME
    #textclass = Textclasses.COUNTRY
    #textclass = Textclasses.COMPANY
    textclass = Textclasses.NUMBER
    #textclass = Textclasses.NATURAL_TEXT
    
    #text_language = "german"
    #stt_language = "german"
    text_language = "english"
    stt_language = "english"
    
    # "amused": 0, "angry": 1, "disgusted": 2, "drunk": 3, "neutral": 4, "sleepy": 5, "surprised": 6, "whisper": 7
    #voice_1_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "de_DE-thorsten_emotional-medium.onnx"))
    #voice_2_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx"))
    
    voice_1_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_GB-northern_english_male-medium.onnx"))
    voice_2_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_GB-southern_english_female-low.onnx"))
    # Indian English: 3
    voice_3_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_US-arctic-medium.onnx"))
    
    voices = [
        (voice_1_path, None),
        (voice_2_path, None),
        (voice_3_path, [3])
    ]

    custom_params = {
        "noise_layers": 0,
        "volumes": [1.0],
        "speeds": [1.0],
        "num_interrupts": 0,
        "len_interrupts": 0.1,
        "snr_lower": 30.0,
        "snr_upper": 40.0,
        "total_snrlevels": 2
    }

    results = generate_phonetic_mistakes(text, textclass, text_language, stt_language, voices, stt_name="Whisper_tiny_en")
    print(results)
    
    '''
    if TEST_CASE:
        test_texts = [("Maria Sklodowska-Curie", Textclasses.NAME)]
        #test_text = ("17534", Textclasses.NUMBER)
        test_language = "german"
        #test_speaker = "Ryan"
        test_voices= [("de_DE-thorsten_emotional-medium.onnx", [1])]
        #test_instruct = ""
        test_sr = 16000

        test_case_piper(test_texts, test_language, test_voices, test_sr)
        


    if not ONLY_TEST:
        """
        original_texts=[
            #"Xi Jinping is the president of China.",
            "Maria Sklodowska-Curie und Mikolaj Kopernik sind berühmte polnische Wissenschaftler.",
            #"L'arc de Triomphe est un monument célèbre à Paris.",
            #"Shigeru Miyamoto ist ein berühmter Entwickler bei Nintendo."
        ]"""

        original_texts=[
            ("Bosnien und Herzegowina", Textclasses.COUNTRY),
            ("Maria Sklodowska-Curie", Textclasses.NAME),
            ("L'arc de Triomphe", Textclasses.COUNTRY),
            ("Samsung", Textclasses.COMPANY),
            ("17543", Textclasses.NUMBER),
            ("siebzehntausendfünfhundertfünfundfünfzig", Textclasses.NUMBER),
            ("ein heißer Mittwochabend mit vielen Eiswürfeln", Textclasses.NATURAL_TEXT)
        ]

        text_language = "german"

        # "amused": 0, "angry": 1, "disgusted": 2, "drunk": 3, "neutral": 4, "sleepy": 5, "surprised": 6, "whisper": 7
        voices = [
            ("de_DE-thorsten_emotional-medium.onnx", [1, 3, 5, 7]),
            ("Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx", None)
        ]

        """if ALL_LANGUAGES:
            languages = "all"
        else:
            languages = [
                #'chinese',
                #'english',
                #'french',
                'german',
                #'japanese'
                ]
        if ALL_SPEAK:       
            speakers = "all"
        else:       
            speakers = ['vivian']
        instructs=[
            "speak slurred and erratic as if drunk, unintelligible and without clear words and with heavy german accent",
            #"speak breathlessly in an extremely high-pitched and squeaky voice"
        ]"""


        #if not ALL_LANGUAGES and not ALL_SPEAK:
        versions = []
        for i in range(len(original_texts)):
            params = PARAMS[original_texts[i][1]]
            num_versions = 0
            for voice in voices:
                num_versions += (len(voice[1]) if voice[1] is not None else 1) * len(params["volumes"]) * len(params["speeds"]) * (2 if params["num_interrupts"] > 0 else 1)
            versions.append(num_versions)
        sr = 16000
        
        audio_data, orig_sr = tts(texts=original_texts, voices=voices)
        audios = [data[0] for data in audio_data]
        audios = [(audios[i], original_texts[i][1]) for i in range(len(audios))]
        if not SKIP_STT:
            texts = stt(audios, language=text_language)
            print(texts)

        """
        if TO_MEMORY:
            test_clean_folder="test_clean"
            test_noisy_folder="Test_NoisySpeech_After"
            test_clean_proc_folder="Test_CleanSpeech_After"
            test_noise_proc_folder="Test_Noise_After"

            if os.path.exists(test_clean_folder):
                shutil.rmtree(test_clean_folder)
            os.makedirs(test_clean_folder)

        
        modified_textclasses = []
        for audio, textclass in audios:
            params = PARAMS[textclass]
            modified_audios = []
            for vol in params["volumes"]:
                for spd in params["speeds"]:
                    modified_audio = modify_audio(audio, volume_factor=vol, speed_factor=spd)
                    modified_textclasses.append(textclass)
                    sf.write(os.path.join(test_clean_folder, f"test_audio_{vol}vol_{spd}spd.wav"), modified_audio, samplerate=orig_sr)
                    if params["num_interrupts"] > 0:
                        modified_audio_interrupted = add_interruptions(modified_audio, orig_sr, interruption_length=params["len_interrupts"], num_interruptions=params["num_interrupts"])
                        modified_textclasses.append(textclass)
                        sf.write(os.path.join(test_clean_folder, f"test_audio_{vol}vol_{spd}spd_{NUM_INTERRUPTS}interrupts.wav"), modified_audio_interrupted, samplerate=orig_sr)
        """

        modified_audios = []
        for audio, textclass in audios:
            params = PARAMS[textclass]
            for vol in params["volumes"]:
                for spd in params["speeds"]:
                    modified_audio = modify_audio(audio, volume_factor=vol, speed_factor=spd)
                    modified_audios.append((modified_audio, textclass))
                    if params["num_interrupts"] > 0:
                        modified_audio_interrupted = add_interruptions(modified_audio, orig_sr, interruption_length=params["len_interrupts"], num_interruptions=params["num_interrupts"])
                        modified_audios.append((modified_audio_interrupted, textclass))
        print(f"Number of modified audio versions: {len(modified_audios)}, expected: {sum(versions)}")
                        
        """
        if len(VOLUMES) > 1 or len(SPEEDS) > 1 or NUM_INTERRUPTS > 0:
            versions_per_text = versions_per_text * len(VOLUMES) * len(SPEEDS) * (2 if NUM_INTERRUPTS > 0 else 1)
            modified_audios = []
            for audio in audios:
                modified_audios.append(modify_audio(audio, volume_factor=VOLUMES[0], speed_factor=SPEEDS[0]))
                if NUM_INTERRUPTS > 0:
                    modified_audios.append(add_interruptions(modified_audios[-1], orig_sr, interruption_length=LEN_INTERRUPTS, num_interruptions=NUM_INTERRUPTS))
            audios = modified_audios
            print(f"Number of modified audio versions: {len(modified_audios)}, versions per text: {versions_per_text}")
        """

        if SYNTHESIZE_NOISE:
            
            for i in range(len(original_texts)):
                params = PARAMS[original_texts[i][1]]
                versions[i] = versions[i] * params["total_snrlevels"]

            audios_by_class = [[]] * len(Textclasses)
            for textclass in Textclasses:
                for audio, t in modified_audios:
                    if textclass == t:
                        audios_by_class[textclass.value].append(audio)
            
            noisy_speech = []
            for textclass in Textclasses:
                params = PARAMS[textclass]
                audios = audios_by_class[textclass.value]
                for i in range(params["noise_layers"]):
                    noisy_speech_textclass, clean_speech, noise = synthesize_noisy_speech(audios = audios, orig_sr=orig_sr, snr_lower=params["snr_lower"], snr_upper=params["snr_upper"], total_snrlevels=params["total_snrlevels"], write_processed_files = True, sampling_rate=sr)
                    noisy_speech.extend(noisy_speech_textclass)
                    audios = noisy_speech_textclass

            noisy_texts = stt(noisy_speech, language=text_language)

            """snr_lower = 10.0
            snr_upper = 20.0
            total_snrlevels = 2
            versions = versions * total_snrlevels

            noisy_speech, clean_speech, noise = synthesize_noisy_speech(audios = audios, orig_sr=orig_sr, snr_lower=snr_lower, snr_upper=snr_upper, total_snrlevels=total_snrlevels, write_processed_files = True, sampling_rate=sr)
            noisy_texts = stt(noisy_speech, language=text_language)
            for i in range(len(noisy_texts)):
                print(f"Transcription for Noisy version {i+1}: {noisy_texts[i]}")
                print(f"Original text: {original_texts[i//versions_per_text]}")
                print(f"Levenshtein distance to original: {Levenshtein.distance(original_texts[i//versions_per_text], noisy_texts[i])}, ratio: {Levenshtein.ratio(original_texts[i//versions_per_text], noisy_texts[i])}")
                print(f"Required Edits: {Levenshtein.editops(original_texts[i//versions_per_text], noisy_texts[i])}")
                print("--------------------------------------------------")""" '''
        
