from pathlib import Path

from audiolib import audioread, audiowrite
from pydub import AudioSegment

input_folder = Path("Input_Fabian/audio_upload")
output_folder = Path("Input_Fabian/audio_upload_wav")
output_folder.mkdir(parents=True, exist_ok=True)

for input_path in input_folder.glob("*.opus"):
    output_path = output_folder / f"{input_path.stem}.wav"

    audio_segment = AudioSegment.from_file(input_path)
    audio_segment.export(output_path, format="wav")

    audio, sr = audioread(output_path)
    audiowrite(audio, sr, output_path)
