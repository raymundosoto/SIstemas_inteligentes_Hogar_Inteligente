from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# Diccionario complejo
# Estructura: {"Nombre_Agente": {"hora": "12:00", "led1": 0, "led2": 1, "led3": 0}}
agentes = {}

@app.route('/')
def index():
    return render_template('index.html', agentes=agentes)

@app.route('/orden', methods=['POST'])
def recibir_orden():
    datos = request.json
    id_esp = datos.get('id_dispositivo') # A qué agente va la orden
    led = datos.get('led')               # led1, led2 o led3
    estado = datos.get('estado')         # 1 o 0
    
    if id_esp in agentes:
        agentes[id_esp][led] = estado
        return jsonify({"status": "Orden enviada a " + id_esp}), 200
    return jsonify({"status": "Agente no encontrado"}), 404

@app.route('/update', methods=['POST'])
def update_status():
    datos = request.json
    id_esp = datos.get('id_dispositivo', 'Desconocido')
    
    tz_mex = pytz.timezone('America/Mexico_City')
    hora_actual = datetime.now(tz_mex).strftime("%H:%M:%S")
    
    # Si el agente es nuevo, le creamos sus estados iniciales en 0
    if id_esp not in agentes:
        agentes[id_esp] = {
            "hora": hora_actual,
            "led1": 0, "led2": 0, "led3": 0
        }
    else:
        agentes[id_esp]["hora"] = hora_actual

    # Le regresamos solo sus propios estados
    return jsonify({
        "led1": agentes[id_esp]["led1"],
        "led2": agentes[id_esp]["led2"],
        "led3": agentes[id_esp]["led3"]
    }), 200

if __name__ == '__main__':
    app.run(debug=True)