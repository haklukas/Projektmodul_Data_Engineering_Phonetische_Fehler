import wave
from piper import PiperVoice, SynthesisConfig
from transformers import AutoProcessor, BarkModel
import scipy
import soundfile as sf
import io

#voice = PiperVoice.load("en_US-lessac-medium.onnx")
#text = "Welcome to the world of speech synthesis!"
voice = PiperVoice.load("de_DE-thorsten_emotional-medium.onnx")
#voice = PiperVoice.load("Thorsten-Voice_Hessisch_Piper_high-Oct2023.onnx")
text = "Michael, the dog is hungry!"


# "amused": 0, "angry": 1, "disgusted": 2, "drunk": 3, "neutral": 4, "sleepy": 5, "surprised": 6, "whisper": 7

syn_config = SynthesisConfig(
    speaker_id=1,
    volume=1,
    length_scale=1,
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

sf.write("pipertest_buffer.wav", data, samplerate)

"""
syn_config = SynthesisConfig(
    volume=0.5,  # half as loud
    length_scale=2.0,  # twice as slow
    noise_scale=1.0,  # more audio variation
    noise_w_scale=1.0,  # more speaking variation
    normalize_audio=False, # use raw audio from voice
)

syn_config = SynthesisConfig(
    volume=1,
    length_scale=1,
    noise_scale=1.0,
    noise_w_scale=1.0,
    normalize_audio=True,
)

with wave.open("pipertest2.wav", "wb") as wav_file:
    voice.synthesize_wav(text, wav_file, syn_config=syn_config)


processor = AutoProcessor.from_pretrained("suno/bark-small")
model = BarkModel.from_pretrained("suno/bark-small")

#voice_preset = "v2/en_speaker_6"
voice_preset = "v2/de_speaker_9"

#inputs = processor("Hello, my dog is cute", voice_preset=voice_preset)
#inputs = processor("Und wenn ich das so rede, dann hört man das schon, dass ich aus Bayern komme.", voice_preset=voice_preset)
#inputs = processor("[with strong bavarian dialect]Und wenn ich das so rede, dann hört man das schon [clears throat], dass ich aus Bayern komme.", voice_preset=voice_preset)
#inputs = processor("[annoyed]Und wenn ich das so rede, dann hört man das schon, dass ich aus Bayern komme.", voice_preset=voice_preset)
inputs = processor("[slurred speech]Und wenn ich das so rede, dann hört man das schon, dass ich aus Bayern komme.", voice_preset=voice_preset)


audio_array = model.generate(**inputs)
audio_array = audio_array.cpu().numpy().squeeze()

sample_rate = model.generation_config.sample_rate
scipy.io.wavfile.write("bark_out5.wav", rate=sample_rate, data=audio_array)"""