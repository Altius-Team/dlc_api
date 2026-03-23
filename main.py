from flask import Flask, jsonify
from flask_cors import CORS
import threading
import time
import os
import json
import requests

from config import SUPABASE_CLIENT, BUCKET_NAME
from fetch_dlc import FetchDLCWiki

app = Flask(__name__)

CORS(app) 
CORS(app, origins=["https://preview.altiusapp.cc", "http://localhost:3000", "https://panel.andevtc.com", "https://preview-tunnel.altiusapp.cc"])

# Ruta en el bucket de Supabase para el JSON de DLC (wiki)
DLC_JSON_PATH = "dlc/wiki_dlc.json"


def update_dlc_wiki():
    """Actualiza el JSON de DLC desde el wiki y lo sube a Supabase."""
    fetcher = FetchDLCWiki()
    data = fetcher.get_all_dlc_json()
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    SUPABASE_CLIENT.storage.from_(BUCKET_NAME).upload(
        path=DLC_JSON_PATH,
        file=json_bytes,
        file_options={"content-type": "application/json", "upsert": "true"},
    )
    print("DLC (wiki) actualizado en Supabase")
    return data


def get_dlc_from_supabase():
    """Descarga el JSON de DLC desde Supabase. Devuelve None si no existe o falla."""
    try:
        data = SUPABASE_CLIENT.storage.from_(BUCKET_NAME).download(DLC_JSON_PATH)
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        print("Error leyendo DLC desde Supabase:", e)
        return None


@app.route("/")
def health():
    return {"status": "running"}


@app.route("/dlc")
def dlc():
    """Devuelve el JSON de DLC (nombre + juego) guardado en Supabase."""
    data = get_dlc_from_supabase()
    if data is None:
        return jsonify({"error": "DLC no disponible. Ejecuta /update-dlc primero."}), 503
    return jsonify(data)


@app.route("/update-dlc")
def update_dlc():
    """Fuerza la actualización del JSON de DLC desde el wiki y lo guarda en Supabase."""
    try:
        data = update_dlc_wiki()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def scheduler():
    """Cada 12h actualiza el JSON de DLC en Supabase."""
    while True:
        try:
            update_dlc_wiki()
        except Exception as e:
            print("Error en scheduler DLC:", e)
        time.sleep(43200)  # 12 horas


def keep_alive():
    """Realiza un ping a la propia URL del servicio cada 14 minutos para evitar que Render apague el servicio."""
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        print("Keep-alive omitido: RENDER_EXTERNAL_URL no configurada")
        return
    
    while True:
        try:
            # Ping a la URL pública para que el balanceador de Render lo cuente como actividad
            response = requests.get(url, timeout=15)
            print(f"[Keep-alive] Ping enviado a {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"[Keep-alive] Error en el ping: {e}")
        
        # Dormir 14 minutos (Render free tier suele apagar tras 15 min de inactividad)
        time.sleep(840)


# En Render puedes desactivar el scheduler y usar un Cron Job que llame a /update-dlc cada 12h
if os.environ.get("ENABLE_DLC_SCHEDULER", "1") == "1":
    threading.Thread(target=scheduler, daemon=True).start()

# Hilo para keep-alive (opcional si se configura RENDER_EXTERNAL_URL)
if os.environ.get("ENABLE_KEEP_ALIVE", "1") == "1":
    threading.Thread(target=keep_alive, daemon=True).start()


if __name__ == "__main__":
    port = os.environ.get("PORT", 5000)
    app.run(host="0.0.0.0", port=port, debug=True)
