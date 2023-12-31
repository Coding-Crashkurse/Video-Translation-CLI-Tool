# Video Audio Translator

## Overview
This Python script automates the process of downloading YouTube videos, extracting audio, transcribing it, converting the transcription to speech, and then reassembling the video with the new audio track.

## Requirements
Requires Python and the following libraries: `typer`, `moviepy`, `pytube`, `python-dotenv`, `openai`.

## Usage
Run the script with:
```bash
python script.py --input-file "path_or_url_to_input" --output-file "output_file_path.mp4" --voice "voice_option"
```

--input-file: Path to a local video file or a YouTube URL. <br>
--output-file: Path for the output video file. <br>
--voice: Voice option for text-to-speech (e.g., "alloy", "echo").