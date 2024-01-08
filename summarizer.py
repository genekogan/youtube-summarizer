from dotenv import load_dotenv
load_dotenv()

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
    
    #whisper_model = whisper.load_model('base')
    #result = whisper_model.transcribe(audio_filename+".mp3")
    #transcript = result['text']

    audio_file = open(audio_filename+".mp3", "rb")

    transcript = client.audio.transcriptions.create(
        model="whisper-1", 
        file=audio_file
    )

    #os.remove(audio_filename+".mp3")

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
