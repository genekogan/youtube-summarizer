from dotenv import load_dotenv
load_dotenv()

import subprocess
import argparse
import os
import uuid
import tempfile
import textwrap
import yt_dlp
#import whisper
import openai

client = openai.OpenAI()

audio_filename = str(uuid.uuid4().hex)

system_prompt = "You are a helpful assistant, whose sole job is to take transcripts and summarize them."
summarize_prompt = "Summarize the following transcript into a list of {num_bullet_points} bullet points.\n\n\nText: {transcript}:"


def pretty_print(text, width):
    lines = text.splitlines()
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
    wrapped_text = '\n'.join(wrapped_lines)
    print(wrapped_text)


def summarize_youtube(url, num_bullet_points):
    
    # Download from YouTube
    ydl_opts = {
        'outtmpl': audio_filename,
        'format': 'worstaudio',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96',
        }],
        'max_filesize': 25*1024*1024  # Set maximum filesize to 25MB
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Convert to mono
    command = [
        'ffmpeg',
        '-i', audio_filename + ".mp3",  # Input file
        '-ac', '1',                     # Set audio channels to 1 (mono)
        '-ab', '32k',                   # Set a lower bitrate, e.g., 32 kbps
        '-y',                           # Overwrite output file if it exists
        audio_filename + "_mono.mp3"    # Output file
    ]

    subprocess.run(command)

    # Transcribe with Whisper
    #whisper_model = whisper.load_model('base')
    #result = whisper_model.transcribe(audio_filename+"_mono.mp3")
    #transcript = result['text']

    audio_file = open(audio_filename+"_mono.mp3", "rb")

    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )

    # clean up
    os.remove(audio_filename+".mp3")
    os.remove(audio_filename+"_mono.mp3")

    # summarize transcript
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": summarize_prompt.format(num_bullet_points=num_bullet_points, transcript=transcript),
            }
        ],
        temperature=0,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    text = response.choices[0].message.content
    return text



def main():
    parser = argparse.ArgumentParser(description='Summarize YouTube videos.')
    parser.add_argument('url', type=str, help='The URL of the YouTube video to summarize.')
    parser.add_argument('num_points', type=int, help='The number of bullet points to summarize the video into.', default=20)
    args = parser.parse_args()

    text = summarize_youtube(args.url, args.num_points)
    pretty_print(text, 80)

if __name__ == "__main__":
    main()
