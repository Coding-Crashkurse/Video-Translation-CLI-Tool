import os
from dotenv import load_dotenv, find_dotenv


import typer
from enum import Enum
from moviepy.editor import AudioFileClip, VideoFileClip
from openai import OpenAI
from pytube import YouTube

load_dotenv(find_dotenv())

app = typer.Typer()

EXTRACTED_AUDIO_FILENAME = "extracted_audio.mp3"
TRANSLATED_SPEECH_FILENAME = "translated_speech.mp3"
DOWNLOADED_VIDEO_FILENAME = "downloaded_video.mp4"

class VoiceOptions(Enum):
    ALLOY = "alloy"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SHIMMER = "shimmer"

def download_youtube_video(url, output_path):
    typer.echo(f"Downloading YouTube video from {url}")
    yt = YouTube(url)
    stream = (
        yt.streams.filter(progressive=True, file_extension="mp4")
        .order_by("resolution")
        .desc()
        .first()
    )
    stream.download(output_path=output_path, filename=DOWNLOADED_VIDEO_FILENAME)
    typer.echo("Download completed.")

def extract_audio_from_video(video_path, audio_path):
    typer.echo(f"Extracting audio from video: {video_path}")
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file {video_path} not found.")

    with VideoFileClip(video_path) as video_clip:
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(audio_path)
    typer.echo("Audio extraction completed.")

def transcribe_audio(openai_client, audio_file_path):
    typer.echo("Transcribing audio...")
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai_client.audio.translations.create(
            model="whisper-1", file=audio_file
        ).text
    typer.echo("Transcription completed.")
    return transcript

def text_to_speech(openai_client, transcript, output_path, voice):
    typer.echo(f"Converting text to speech using voice: {voice}...")
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=transcript
    )
    response.stream_to_file(output_path)
    typer.echo("Text-to-speech conversion completed.")

def create_video_with_new_audio(video_path, audio_path, output_video_path):
    typer.echo("Creating new video with the converted audio...")
    with VideoFileClip(video_path) as video_clip, AudioFileClip(audio_path) as new_audio_clip:
        final_video = video_clip.set_audio(new_audio_clip)
        final_video.write_videofile(output_video_path)
    typer.echo("New video creation completed.")

@app.command()
def main(
    input_file: str = typer.Option(
        ..., "--input-file", "-i", help="Input file path or YouTube URL"
    ),
    output_file: str = typer.Option(
        "video.mp4", "--output-file", "-o", help="Output file path"
    ),
    voice: VoiceOptions = typer.Option(
        VoiceOptions.ALLOY, "--voice", "-v", help="Voice for text-to-speech"
    ),
    cleanup: bool = typer.Option(True, "--cleanup", help="Cleanup temporary files"),
):
    client = OpenAI()

    # Check if input is a URL
    if input_file.startswith("http://") or input_file.startswith("https://"):
        typer.echo("Input is a URL, proceeding to download the video.")
        download_youtube_video(input_file, os.getcwd())
        video_path = os.path.join(os.getcwd(), DOWNLOADED_VIDEO_FILENAME)
    else:
        video_path = input_file

    extracted_audio_path = os.path.join(os.getcwd(), EXTRACTED_AUDIO_FILENAME)
    translated_speech_path = os.path.join(os.getcwd(), TRANSLATED_SPEECH_FILENAME)
    new_video_path = output_file

    extract_audio_from_video(video_path, extracted_audio_path)
    transcript = transcribe_audio(client, extracted_audio_path)
    text_to_speech(client, transcript, translated_speech_path, voice.value)
    create_video_with_new_audio(video_path, translated_speech_path, new_video_path)

    if cleanup:
        typer.echo("Cleaning up temporary files...")
        if input_file.startswith("http://") or input_file.startswith("https://"):
            os.remove(video_path)
        os.remove(extracted_audio_path)
        if os.path.exists(translated_speech_path):
            os.remove(translated_speech_path)
        typer.echo("Cleanup completed.")

    typer.echo("Process completed successfully.")

if __name__ == "__main__":
    app()