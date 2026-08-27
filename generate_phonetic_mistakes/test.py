import wave
from piper import PiperVoice, SynthesisConfig
import soundfile as sf
import io
import os
import numpy as np
from tts import tts_piper_single
import phonetics
import textdistance
from generate_phonetic_mistakes import pick_mistake

#print(np.array([('a', 1), ("b", 2)], dtype=np.dtype('U50, float')))

#print(textdistance.DamerauLevenshtein().distance('text', 'test'))

t = [1, 2, 3]
x = ["x1", "x2", "x3"]

x2 = []
t2 = []
for i in range(len(x)):
    x2.append(x[i] + "1")
    t2.append(t[i])
    x2.append(x[i] + "2")
    t2.append(t[i])

print(x2)
print(t2)

x3 = []
t3 = []

step = 0
for i in range(2):
    new = []
    for j in range(len(x2)):
        new.append(x2[j] + "1")
        new.append(x2[j] + "2")
        new.append(x2[j] + "3")
        new.append(x2[j] + "4")
    print(f"new: {new}")
    x3.extend(new)
    print(f"x3: {x3}")
    print("##########################################")
    print(f"Number of new noisy speech versions after layer {step}: {len(new)}")
    print(f"Len of audios after layer {step}: {len(x2)}")
    noisy_versions_per_clean_audio = len(new) // len(x2)
    print(f"Number of noisy versions per clean audio: {noisy_versions_per_clean_audio}")
    print(len(new) / len(x2))
    t3.extend([md for md in t2 for _ in range(noisy_versions_per_clean_audio)])
    print(len(t3))
    print(f"t3: {t3}")
    print("##########################################")
    step = step + 1
    x2 = x3.copy()
    t2 = t3.copy()

for i in range(len(x3)):
    print(f"x3: {x3[i]}, t3: {t3[i]}")
"""
text = "test"

noisy_texts = ["test", "text", "Treff", "taff", "teste", "trist", "rest", "klec", "djsakl"]

pick_mistake(text, noisy_texts, "german", 5)


#voice = PiperVoice.load("en_US-lessac-medium.onnx")
#text = "Welcome to the world of speech synthesis!"
voice_1_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "de_DE-thorsten_emotional-medium.onnx"))
    
voice = PiperVoice.load(voice_1_path)
#voice = PiperVoice.load("Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx")
text = "Hallo, ich bin im Speicher!"


# "amused": 0, "angry": 1, "disgusted": 2, "drunk": 3, "neutral": 4, "sleepy": 5, "surprised": 6, "whisper": 7

syn_config = SynthesisConfig(
    speaker_id=1,
    volume=1,
    length_scale=0.5,
    noise_scale=1.0,
    noise_w_scale=1.0,
    normalize_audio=True,
)

with wave.open("pipertest_id1.wav", "wb") as wav_file:
    voice.synthesize_wav(text, wav_file, syn_config=syn_config)


buffer = io.BytesIO()

with wave.open(buffer, "wb") as wav_file:
    voice.synthesize_wav("Hallo, ich bin im Speicher!", wav_file, syn_config=syn_config)

wav_bytes = buffer.getvalue()

data, samplerate = sf.read(io.BytesIO(wav_bytes))

sf.write("pipertest_buffer.wav", data, samplerate)"""