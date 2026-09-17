import csv
import os
import shutil
from pathlib import Path

from generate_phonetic_mistakes import get_phonetic_mistake_single
from textclass_params import Textclasses


def create_survey_data_noisy(
	texts,
	textclasses,
	text_language,
	stt_language,
	voices,
	severity,
	tts_name="Piper",
	stt_name="Whisper_turbo",
	csv_path="survey_data_noisy.csv",
	audio_output_dir="survey_audio_noisy",
):
	"""Create or append noisy survey examples to a CSV file."""
	if len(texts) != len(textclasses):
		raise ValueError("texts and textclasses must have the same length")

	output_path = Path(csv_path)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	audio_output_path = Path(audio_output_dir)
	audio_output_path.mkdir(parents=True, exist_ok=True)
	write_header = not output_path.exists() or output_path.stat().st_size == 0

	with output_path.open("a", newline="", encoding="utf-8") as csv_file:
		writer = csv.DictWriter(
			csv_file,
			fieldnames=["text", "noisy_text", "filename"],
		)
		if write_header:
			writer.writeheader()

		for text, textclass in zip(texts, textclasses):
			result = get_phonetic_mistake_single(
				text=text,
				textclass=textclass,
				text_language=text_language,
				stt_language=stt_language,
				voices=voices,
				severity=severity,
				tts_name=tts_name,
				stt_name=stt_name,
				return_filename=True,
			)
			if result is None:
				continue

			noisy_text, filename = result
			if filename is None:
				continue

			source_audio_path = Path(filename)
			if not source_audio_path.exists():
				raise FileNotFoundError(f"Generated noisy audio does not exist: {source_audio_path}")

			file_number = 0
			survey_audio_path = audio_output_path / f"survey_noisy_{file_number}.wav"
			while survey_audio_path.exists():
				file_number += 1
				survey_audio_path = audio_output_path / f"survey_noisy_{file_number}.wav"
			shutil.copy2(source_audio_path, survey_audio_path)

			writer.writerow(
				{
					"text": text,
					"noisy_text": noisy_text,
					"filename": str(survey_audio_path),
				}
			)

if __name__ == "__main__":
	
    # Example usage
    texts = ["Hello world", "19573"]
    textclasses = [Textclasses.NATURAL_TEXT, Textclasses.NUMBER]
    text_language = "english"
    stt_language = "english"
    voice_3_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_US-arctic-medium.onnx"))

    voices = [
        (voice_3_path, None),
    ]
    severity = 1
    create_survey_data_noisy(
        texts,
        textclasses,
        text_language,
        stt_language,
        voices,
        severity,
        csv_path="survey_data_noisy.csv",
    )