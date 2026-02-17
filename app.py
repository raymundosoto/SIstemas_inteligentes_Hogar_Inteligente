from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Diccionario para guardar agentes de forma independiente
# Estructura: {"Nombre": {"hora": "...", "led1": 0, "led2": 0, "led3": 0}}
agentes = {}

@app.route('/')
def index():
    # Pasamos el diccionario 'agentes' al HTML
    return render_template('index.html', agentes=agentes)

@app.route('/update', methods=['POST'])
def update_status():
    datos = request.json
    id_esp = datos.get('id_dispositivo', 'Desconocido')
    
    # Aseguramos que los valores sean enteros (0 o 1) para que el HTML los entienda
    agentes[id_esp] = {
        "hora": datetime.now().strftime("%H:%M:%S"),
        "led1": int(datos.get('led1', 0)),
        "led2": int(datos.get('led2', 0)),
        "led3": int(datos.get('led3', 0))
    }
    return jsonify({"status": "recibido"}), 200

# Esta ruta es para que la App o el CMD cambien el estado
@app.route('/orden', methods=['POST'])
def recibir_orden():
    datos = request.json
    id_esp = datos.get('id_dispositivo')
    led = datos.get('led')      # Ejemplo: "led1"
    estado = datos.get('estado') # 1 o 0
    
    if id_esp in agentes:
        agentes[id_esp][led] = int(estado)
        return jsonify({"status": "ok"}), 200
    return jsonify({"error": "Agente no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)