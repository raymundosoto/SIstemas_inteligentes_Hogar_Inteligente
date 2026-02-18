from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Almacenamos datos de agentes, actuadores y clima
agentes = {}

@app.route('/')
def index():
    return render_template('index.html', agentes=agentes)

@app.route('/update', methods=['POST'])
def update_status():
    datos = request.json
    id_esp = datos.get('id_dispositivo', 'Desconocido')
    
    agentes[id_esp] = {
        "hora": datetime.now().strftime("%H:%M:%S"),
        "temp": datos.get('temp', 0),
        "hum": datos.get('hum', 0),
        "viento": datos.get('viento', 0),
        "act1": int(datos.get('act1', 0)), # Ventilador
        "act2": int(datos.get('act2', 0)), # Humidificador
        "act3": int(datos.get('act3', 0))  # Iluminación
    }
    return jsonify({"status": "recibido"}), 200

if __name__ == '__main__':
    app.run(debug=True)