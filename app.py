from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz

app = Flask(__name__)

# Diccionario maestro: guarda los datos de cada agente por separado
# Ejemplo: {'Agente1': {'hora': '10:00', 'led1': 0...}, 'Agente2': {...}}
base_datos_agentes = {}

@app.route('/')
def index():
    # Enviamos todo el diccionario para generar los paneles en el HTML
    return render_template('index.html', agentes=base_datos_agentes)

@app.route('/orden', methods=['POST'])
def recibir_orden():
    datos = request.json
    id_esp = datos.get('id_dispositivo')
    led = datos.get('led')
    estado = datos.get('estado')
    
    # Solo damos ordenes a agentes que ya se hayan registrado (conectado)
    if id_esp in base_datos_agentes:
        base_datos_agentes[id_esp][led] = estado
        return jsonify({"status": "Orden enviada a " + id_esp}), 200
    return jsonify({"status": "Error: Agente no encontrado"}), 404

@app.route('/update', methods=['POST'])
def update_status():
    datos = request.json
    id_esp = datos.get('id_dispositivo', 'Desconocido')
    
    # Hora de la Ciudad de Mexico
    tz_mex = pytz.timezone('America/Mexico_City')
    hora_actual = datetime.now(tz_mex).strftime("%H:%M:%S")
    
    # Si es la primera vez que vemos a este agente, le creamos su panel
    if id_esp not in base_datos_agentes:
        base_datos_agentes[id_esp] = {
            "hora": hora_actual,
            "led1": 0, "led2": 0, "led3": 0
        }
    else:
        # Si ya existe, solo actualizamos su hora de conexion
        base_datos_agentes[id_esp]["hora"] = hora_actual

    # Le regresamos al ESP32 solo SUS estados
    return jsonify({
        "led1": base_datos_agentes[id_esp]["led1"],
        "led2": base_datos_agentes[id_esp]["led2"],
        "led3": base_datos_agentes[id_esp]["led3"]
    }), 200

if __name__ == '__main__':
    app.run(debug=True)