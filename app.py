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
    # Si no llega el id_dispositivo, no hacemos nada
    if not datos or 'id_dispositivo' not in datos:
        return jsonify({"error": "Faltan datos"}), 400
    
    id_esp = datos.get('id_dispositivo')
    hora_actual = datetime.now().strftime("%H:%M:%S")

    # Guardamos o actualizamos los datos del agente
    # Usamos .get(llave, 0) para que si no viene el dato, por defecto sea 0 (apagado)
    agentes[id_esp] = {
        "hora": hora_actual,
        "led1": int(datos.get('led1', 0)),
        "led2": int(datos.get('led2', 0)),
        "led3": int(datos.get('led3', 0))
    }
    
    print(f"Actualizacion recibida de {id_esp}: {agentes[id_esp]}")
    return jsonify(agentes[id_esp]), 200

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