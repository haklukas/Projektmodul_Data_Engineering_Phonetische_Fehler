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
        "noise_layers": 1,
        "volumes": [1.0],
        "speeds": [1.0],
        "num_interrupts": 0,
        "len_interrupts": 0.1,
        "snr_lower": 30.0,
        "snr_upper": 40.0,
        "total_snrlevels": 2
    }

    results = generate_phonetic_mistakes(text, textclass, text_language, stt_language, voices, severity=3, stt_name="Whisper_tiny_en")
    print(results)