from flask import Flask, request, send_file, jsonify
import yt_dlp
import uuid
import os

app = Flask(__name__)

# 🔍 SEARCH
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return {"error": "Query mancante"}, 400

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            for entry in info['entries']:
                results.append({
                    "title": entry.get("title"),
                    "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                    "id": entry.get("id"),
                    "thumbnail": entry.get("thumbnail"),
                })
        return jsonify(results)
    except Exception as e:
        return {"error": str(e)}, 500

# ▶️ STREAM (riproduzione diretta)
@app.route('/stream', methods=['POST'])
def stream_audio():
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
        return send_file(filename, mimetype='audio/mpeg', as_attachment=False)
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# ⬇️ DOWNLOAD (come prima, ma separato)
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

# Avvia il server su Render
app.run(host='0.0.0.0', port=10000)
