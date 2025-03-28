from flask import Flask, request, send_file, jsonify
import yt_dlp
import uuid
import os
import tempfile

app = Flask(__name__)

# ✅ Cookie support
temp_dir = tempfile.gettempdir()
cookie_file = "/opt/render/project/src/cookies.txt"

# Verifica che il file cookies.txt esista
if os.path.exists(cookie_file):
    print("✅ Il file 'cookies.txt' è stato trovato e verrà utilizzato.")
    with open(cookie_file, "r", encoding="utf-8") as f:
        print("📂 Contenuto di cookies.txt:")
        print(f.read())
else:
    print("❌ ERRORE: Il file 'cookies.txt' non è stato trovato. Assicurati che sia nella directory giusta.")

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
        'cookiefile': cookie_file
    }

    results = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch10:{query}", download=False)
            for entry in info['entries']:
                entry_type = "playlist" if entry.get("ie_key") == "YoutubePlaylist" else "video"
                url = f"https://www.youtube.com/watch?v={entry.get('id')}" if entry_type == "video" else f"https://www.youtube.com/playlist?list={entry.get('id')}"
                results.append({
                    "title": entry.get("title"),
                    "url": url,
                    "id": entry.get("id"),
                    "type": entry_type,
                    "thumbnail": entry.get("thumbnail")
                })
        return jsonify(results)
    except Exception as e:
        return {"error": str(e)}, 500

# ▶️ STREAM
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
        'cookiefile': cookie_file,
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

# ⬇️ DOWNLOAD
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
        'cookiefile': cookie_file,
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

# 💽 PLAYLIST (elenco brani da una playlist YouTube)
@app.route('/playlist', methods=['POST'])
def playlist():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return {"error": "URL mancante"}, 400

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
        'cookiefile': cookie_file
    }

    tracks = []
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get('_type') == 'playlist':
                for entry in info['entries']:
                    tracks.append({
                        "title": entry.get("title"),
                        "url": f"https://www.youtube.com/watch?v={entry.get('id')}",
                        "id": entry.get("id"),
                        "thumbnail": entry.get("thumbnail")
                    })
            else:
                return {"error": "Il link non è una playlist"}, 400
        return jsonify(tracks)
    except Exception as e:
        return {"error": str(e)}, 500

# Avvia il server su Render
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
