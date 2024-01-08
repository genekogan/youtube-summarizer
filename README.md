# youtube_summarizer

Downloads with yt_dlp, sends audio to OpenAI whisper for transcription, then summarizes with GPT-4. 

## Install

    pip install -r requirements.txt

## Run

Put your OpenAI key in .env and run:

    python summarizer.py "YOUTUBE_VIDEO_URL" NUMBER_OF_BULLET_POINTS
