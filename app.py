from flask import Flask, render_template, request, jsonify
from datetime import datetime
import pytz # Para asegurar la hora local de México

app = Flask(__name__)

# Diccionario para dispositivos y sus horas de conexion
dispositivos_activos = {}

# Estados de los actuadores (0 apagado, 1 encendido)
estados_hogar = {"led1": 0, "led2": 0, "led3": 0}

@app.route('/')
def index():
    return render_template('index.html', dispositivos=dispositivos_activos, focos=estados_hogar)

@app.route('/orden', methods=['POST'])
def recibir_orden():
    datos = request.json
    led = datos.get('led')
    estado = datos.get('estado')
    if led in estados_hogar:
        estados_hogar[led] = estado
        return jsonify({"status": "ok"}), 200
    return jsonify({"status": "error"}), 400

@app.route('/update', methods=['POST'])
def update_status():
    datos = request.json
    id_esp = datos.get('id_dispositivo', 'Desconocido')
    
    # Configuramos la zona horaria de CDMX
    tz_mex = pytz.timezone('America/Mexico_City')
    hora_actual = datetime.now(tz_mex).strftime("%H:%M:%S")
    
    dispositivos_activos[id_esp] = hora_actual
    
    # Respondemos al ESP32 con las ordenes de los focos
    return jsonify(estados_hogar), 200

if __name__ == '__main__':
    app.run(debug=True)