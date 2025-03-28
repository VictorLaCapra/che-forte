from flask import Flask, request, send_file, jsonify
import yt_dlp
import uuid
import os

app = Flask(__name__)

# Indica il percorso del file cookies.txt
cookie_file = "/opt/render/project/src/cookies.txt"

if not os.path.exists(cookie_file):
    print("❌ Il file 'cookies.txt' non è stato trovato. Controlla il percorso e riprova.")
else:
    print("✅ Il file 'cookies.txt' è stato trovato e verrà utilizzato.")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
