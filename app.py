from flask import Flask, request, jsonify, session
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # ¡Importante para usar session!

# Inicializar el estado del bot
bot_status = {"activo": False, "ultima_actividad": None}

@app.route("/")
def index():
    return "¡Hola!"

@app.route("/bot/fetch/status", methods=["POST"])
def actualizar_estado_bot():
    data = request.get_json()
    if not data:
        return jsonify({"status": False, "mensaje": "No se recibió información"}), 400
    # Actualizar el estado del bot
    bot_status["activo"] = True
    bot_status["ultima_actividad"] = datetime.now(timezone.utc)
    print("✅ Estado del bot actualizado")
    return jsonify({"status": True, "mensaje": "Estado actualizado correctamente"}), 200

@app.route("/bot/status", methods=["GET"])
def obtener_status():
    now = datetime.now(timezone.utc)
    session['ultima_actividad'] = bot_status["ultima_actividad"]
    ultima = session.get('ultima_actividad')

    # Marcar como inactivo si pasó mucho tiempo sin actividad
    if ultima and (now - ultima > timedelta(minutes=1)):
        bot_status["activo"] = False

    return jsonify({
        "activo": bot_status["activo"],
        "ultima_actividad": ultima.isoformat() if ultima else None
    })

if __name__ == '__main__':
    app.run(debug=True)