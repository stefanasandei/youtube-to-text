from flask import Flask, request, render_template, redirect
from werkzeug.utils import secure_filename
from sqlalchemy import select
from sqlalchemy.orm import Session
import yt_dlp
import whisper
import threading
import requests
import os

from src.models import Video, generate_schema, get_conn, engine

app = Flask(__name__)
connection = get_conn()
whisper_model = whisper.load_model("small")

@app.route("/", methods=['GET', 'POST'])
def index():
    with Session(engine) as session:
        results = session.query(Video).all()
        return render_template('index.html', videos=results, new_video=(request.method == 'POST'))

@app.route("/video", methods=['GET', 'POST'])
def video():
    if request.method == 'POST':
        url = request.form['url']

        t = threading.Thread(target=upload_video, args=(url,))
        t.start()

        return redirect("/", code=307)

    with Session(engine) as session:
        id = request.args["id"]
        result = session.query(Video).filter_by(id=id).first()
        if not result:
            return redirect('/')
        return render_template("video.html", video=result)

@app.route("/test_db")
def test_db():
    with Session(engine) as session:
        results = session.query(Video).all()
        return str(results)

@app.route("/about")
def about():
    return render_template("about.html")

def upload_video(url):
    print("---- Downloading Audio ----")

    with yt_dlp.YoutubeDL({}) as ydl:
        result = ydl.extract_info(url, download=False)
        if 'entries' in result:
            yt_video = result['entries'][0]
        else:
            yt_video = result

    id = yt_video.get('id', None)
    title = yt_video.get('title', None)
    thumbnail_url = f"https://i.ytimg.com/vi/{id}/maxresdefault.jpg"

    if requests.get(thumbnail_url).status_code == 404:
        thumbnail_url = f"https://i.ytimg.com/vi/{id}/hqdefault.jpg"

    ydl_opts = {
        'outtmpl': 'res/audio/%(id)s.%(ext)s',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as _ydl:
        _ydl.download([url])

    print("---- Transcribing Audio ----")

    whisper_result = whisper_model.transcribe(f"./res/audio/{id}.mp3")
    print(whisper_result)

    with Session(engine) as session:
        new_video = Video(
            id=id,
            name=title,
            thumbnail=thumbnail_url,
            transcoded_text=whisper_result['text']
        )
        session.add(new_video)
        session.commit()

def init():
    generate_schema()
    return app
