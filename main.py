from flask import Flask, request, send_file
import yt_dlp
import uuid
import os

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download_audio():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return {"error": "URL mancante"}, 400

    filename = f"{uuid.uuid4()}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

app.run(host='0.0.0.0', port=10000)
