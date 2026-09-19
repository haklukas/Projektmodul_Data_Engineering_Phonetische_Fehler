import csv
import os
import shutil
from pathlib import Path

import soundfile as sf

from generate_phonetic_mistakes import get_phonetic_mistake_single
from stt import stt
from textclass_params import CLEAN_TEXTCLASS, Textclasses


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


def create_survey_data_clean(
	texts,
	text_language,
	stt_language,
	voices,
	severity=1,
	tts_name="Piper",
	stt_name="Whisper_turbo",
	csv_path="survey_data_clean.csv",
	audio_output_dir="survey_audio_clean",
):
	"""Create or append clean survey examples to a CSV file."""
	output_path = Path(csv_path)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	audio_output_path = Path(audio_output_dir)
	audio_output_path.mkdir(parents=True, exist_ok=True)
	write_header = not output_path.exists() or output_path.stat().st_size == 0

	with output_path.open("a", newline="", encoding="utf-8") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=["text", "clean_text", "filename"])
		if write_header:
			writer.writeheader()

		for text in texts:
			result = get_phonetic_mistake_single(
				text=text,
				textclass=CLEAN_TEXTCLASS,
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

			clean_text, filename = result
			if filename is None:
				continue

			source_audio_path = Path(filename)
			if not source_audio_path.exists():
				raise FileNotFoundError(f"Generated clean audio does not exist: {source_audio_path}")

			file_number = 0
			survey_audio_path = audio_output_path / f"survey_clean_{file_number}.wav"
			while survey_audio_path.exists():
				file_number += 1
				survey_audio_path = audio_output_path / f"survey_clean_{file_number}.wav"
			shutil.copy2(source_audio_path, survey_audio_path)

			writer.writerow(
				{"text": text, "clean_text": clean_text, "filename": str(survey_audio_path)}
			)


def create_survey_data_noisy_from_oclc(
	oclc_csv_path,
	text_language,
	stt_language,
	voices,
	severity,
	tts_name="Piper",
	stt_name="Whisper_turbo",
	csv_path="survey_data_noisy.csv",
	audio_output_dir="survey_audio_noisy",
):
	"""Create survey data from the first ten rows of an OCLC library CSV."""
	texts = []
	textclasses = []

	with Path(oclc_csv_path).open(newline="", encoding="utf-8-sig") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in list(reader)[:10]:
			texts.extend(
				[
					row["Title"],
					row["Publisher"],
					row["Publish Year"],
				]
			)
			textclasses.extend(
				[
					Textclasses.NATURAL_TEXT,
					Textclasses.NAME,
					Textclasses.NUMBER,
				]
			)

	return create_survey_data_noisy(
		texts=texts,
		textclasses=textclasses,
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=severity,
		tts_name=tts_name,
		stt_name=stt_name,
		csv_path=csv_path,
		audio_output_dir=audio_output_dir,
	)

def create_survey_data_clean_from_oclc(
	oclc_csv_path,
	text_language,
	stt_language,
	voices,
	severity=1,
	tts_name="Piper",
	stt_name="Whisper_turbo",
	csv_path="survey_data_clean.csv",
	audio_output_dir="survey_audio_clean",
):
	"""Create clean survey data from the first ten rows of an OCLC library CSV."""
	texts = []

	with Path(oclc_csv_path).open(newline="", encoding="utf-8-sig") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in list(reader)[:10]:
			texts.extend([row["Title"], row["Publisher"], row["Publish Year"]])

	return create_survey_data_clean(
		texts=texts,
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=severity,
		tts_name=tts_name,
		stt_name=stt_name,
		csv_path=csv_path,
		audio_output_dir=audio_output_dir,
	)


def _read_ncvoter_texts(ncvoter_csv_path, limit=10):
	texts = []
	textclasses = []

	with Path(ncvoter_csv_path).open(newline="", encoding="utf-8-sig") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in list(reader)[:limit]:
			texts.extend([row["Name"], row["County"], row["City"], row["Age"]])
			textclasses.extend(
				[
					Textclasses.NAME,
					Textclasses.NAME,
					Textclasses.NAME,
					Textclasses.NUMBER,
				]
			)

	return texts, textclasses


def create_survey_data_noisy_from_ncvoter(
	ncvoter_csv_path,
	text_language,
	stt_language,
	voices,
	severity,
	tts_name="Piper",
	stt_name="Whisper_turbo",
	csv_path="survey_data_noisy_ncvoter.csv",
	audio_output_dir="survey_audio_noisy_ncvoter",
):
	"""Create noisy survey data from the first ten NC voter rows."""
	texts, textclasses = _read_ncvoter_texts(ncvoter_csv_path)
	return create_survey_data_noisy(
		texts=texts,
		textclasses=textclasses,
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=severity,
		tts_name=tts_name,
		stt_name=stt_name,
		csv_path=csv_path,
		audio_output_dir=audio_output_dir,
	)


def create_survey_data_clean_from_ncvoter(
	ncvoter_csv_path,
	text_language,
	stt_language,
	voices,
	severity=1,
	tts_name="Piper",
	stt_name="Whisper_turbo",
	csv_path="survey_data_clean_ncvoter.csv",
	audio_output_dir="survey_audio_clean_ncvoter",
):
	"""Create clean survey data from the first ten NC voter rows."""
	texts, _ = _read_ncvoter_texts(ncvoter_csv_path)
	return create_survey_data_clean(
		texts=texts,
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=severity,
		tts_name=tts_name,
		stt_name=stt_name,
		csv_path=csv_path,
		audio_output_dir=audio_output_dir,
	)


def create_stt_csv_from_wav_folder(
	audio_folder,
	stt_language=None,
	stt_name="Whisper_tiny",
	csv_path=None,
):
	"""Transcribe WAV files in a folder and save their filenames and text to CSV."""
	audio_folder_path = Path(audio_folder)
	if not audio_folder_path.is_dir():
		raise NotADirectoryError(f"Audio folder does not exist: {audio_folder_path}")

	wav_paths = sorted(
		(path for path in audio_folder_path.iterdir() if path.is_file() and path.suffix.lower() == ".wav"),
		key=lambda path: path.name.casefold(),
	)
	if csv_path is None:
		csv_path = audio_folder_path / "stt_results.csv"
	else:
		csv_path = Path(csv_path)

	transcriptions = stt(
		[str(path) for path in wav_paths],
		language=stt_language,
		stt_name=stt_name,
	)
	if len(transcriptions) != len(wav_paths):
		raise RuntimeError(
			f"STT returned {len(transcriptions)} results for {len(wav_paths)} audio files"
		)

	csv_path.parent.mkdir(parents=True, exist_ok=True)
	with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=["filename", "stt_text"])
		writer.writeheader()
		for wav_path, stt_text in zip(wav_paths, transcriptions):
			writer.writerow({"filename": wav_path.name, "stt_text": stt_text})

	return csv_path


def trim_wav_files_in_folder(
	audio_folder,
	output_folder,
	trim_start_seconds=0.1,
	trim_end_seconds=0.1,
):
	"""Trim WAV files and write them with the same names to another folder."""
	if trim_start_seconds < 0 or trim_end_seconds < 0:
		raise ValueError("Trim durations must not be negative")

	audio_folder_path = Path(audio_folder)
	if not audio_folder_path.is_dir():
		raise NotADirectoryError(f"Audio folder does not exist: {audio_folder_path}")

	output_folder_path = Path(output_folder)
	output_folder_path.mkdir(parents=True, exist_ok=True)
	trimmed_paths = []

	for wav_path in sorted(
		(
			path
			for path in audio_folder_path.iterdir()
			if path.is_file() and path.suffix.lower() == ".wav"
		),
		key=lambda path: path.name.casefold(),
	):
		info = sf.info(wav_path)
		start_frames = round(trim_start_seconds * info.samplerate)
		end_frames = round(trim_end_seconds * info.samplerate)
		if start_frames + end_frames >= info.frames:
			raise ValueError(
				f"Trim duration is too long for {wav_path.name}: "
				f"{info.frames} frames available, {start_frames + end_frames} requested"
			)

		audio, samplerate = sf.read(wav_path)
		end_frame = len(audio) - end_frames if end_frames else None
		trimmed_audio = audio[start_frames:end_frame]
		output_path = output_folder_path / wav_path.name
		sf.write(output_path, trimmed_audio, samplerate, subtype=info.subtype)
		trimmed_paths.append(output_path)

	return trimmed_paths

if __name__ == "__main__":

	text_language = "english"
	stt_language = "english"

	wav_folder1 = Path("website_audio_survey/audio_clean/audios")
	wav_folder2 = Path("website_audio_survey/audio_dirty/audios")

	create_stt_csv_from_wav_folder(wav_folder1, stt_language=stt_language)
	create_stt_csv_from_wav_folder(wav_folder2, stt_language=stt_language)

	#wav_folder_begin = Path("website_audio_survey/audio_dirty/audios_to_trim_begin")
	#wav_folder_end = Path("website_audio_survey/audio_dirty/audios_to_trim_end")

	#trim_folder = Path("website_audio_survey/audio_dirty/audios_trimmed")

	#trim_wav_files_in_folder(wav_folder_begin, trim_folder, trim_start_seconds=0.1, trim_end_seconds=0)
	#trim_wav_files_in_folder(wav_folder_end, trim_folder, trim_start_seconds=0, trim_end_seconds=0.1)

	"""
	voice_1_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_GB-northern_english_male-medium.onnx"))
	voice_2_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_GB-southern_english_female-low.onnx"))
	voice_3_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "piper_voices", "en_US-arctic-medium.onnx"))

	
	voices = [
		(voice_1_path, None),
		(voice_2_path, None),
		(voice_3_path, [3]),
	]

	
	create_survey_data_clean_from_ncvoter(
		ncvoter_csv_path=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "parsed_ncvoter_subset.csv")),
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=1,
		csv_path="survey_data_clean_ncvoter.csv",
	)

	create_survey_data_clean_from_oclc(
		oclc_csv_path=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "oclc_library_100.csv")),
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=1,
		csv_path="survey_data_clean.csv",
	)
	

	create_survey_data_noisy_from_oclc(
		oclc_csv_path=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "oclc_library_100.csv")),
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=1,
		csv_path="survey_data_noisy.csv",
	)

	create_survey_data_noisy_from_ncvoter(
		ncvoter_csv_path=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "parsed_ncvoter_subset.csv")),
		text_language=text_language,
		stt_language=stt_language,
		voices=voices,
		severity=1,
		csv_path="survey_data_noisy_ncvoter.csv",
	)
	"""

