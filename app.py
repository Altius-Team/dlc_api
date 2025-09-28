from flask import Flask, request, jsonify, session
from datetime import datetime, timezone, timedelta
import os  # Importa la librería os para acceder a las variables de entorno

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'clave_secreta') # Obtén la clave secreta de las variables de entorno

bot_status = {"activo": False, "ultima_actividad": None}
CONDUCTORES = {}

@app.route("/")
def recibir_mensaje():
    return jsonify({"status": False, "mensaje": "No tienes permisos para ver este contenido"}), 403

@app.route("/aom/bot/fetch/status", methods=["POST"])
def actualizar_estado_bot():
    data = request.get_json()
    if not data:
        return jsonify({"status": False, "mensaje": "No se recibió información"}), 400
    bot_status["activo"] = True
    bot_status["ultima_actividad"] = datetime.now(timezone.utc)
    print("✅ Estado del bot actualizado")
    return jsonify({"status": True, "mensaje": "Estado actualizado correctamente"}), 200

@app.route("/aom/bot/status", methods=["GET"])
def obtener_status():
    now = datetime.now(timezone.utc)
    session['ultima_actividad'] = bot_status["ultima_actividad"]
    ultima = session.get('ultima_actividad')

    if ultima and (now - ultima > timedelta(minutes=1)):
        bot_status["activo"] = False

    return jsonify({
        "activo": bot_status["activo"],
        "ultima_actividad": ultima.isoformat() if ultima else None
    })
    
@app.route("/aom/bot/fetch/conductores", methods=["POST"])
def post_conductores():
    data = request.get_json()
    if not data:
        return jsonify({"error": True, "mensaje": "No se recibió información"}), 400
    CONDUCTORES.update(data)
    print("✅ Conductores actualizados:", CONDUCTORES)
    return jsonify({"error": False, "mensaje": "Conductores actualizados correctamente"}), 200

@app.route("/aom/bot/conductores", methods=["GET"])
def get_conductores():
    if not CONDUCTORES:
        return jsonify({"error": True, "mensaje": "No hay conductores disponibles"}), 404
    return jsonify({"error": False, "drivers": CONDUCTORES}), 200


if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)  # Obtén el puerto de la variable de entorno PORT, usa 5000 por defecto localmente
    app.run(host='0.0.0.0', port=port, debug=True) # Escucha en todas las interfaces y en el puerto asignado