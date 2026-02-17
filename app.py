from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Diccionario para guardar qué aparatos están conectados
dispositivos_en_linea = {}

# Estados de los focos (0 es apagado, 1 es prendido)
# Esto lo lee el ESP32 y lo cambia la App
estados_focos = {"led1": 0, "led2": 0, "led3": 0}

@app.route('/')
def home():
    # Esta página muestra el tablero de control
    return render_template('index.html', dispositivos=dispositivos_en_linea, focos=estados_focos)

@app.route('/orden', methods=['POST'])
def recibir_orden():
    # La App de celular manda aquí si queremos prender un foco
    datos = request.json
    foco = datos.get('led')
    estado = datos.get('estado')
    
    if foco in estados_focos:
        estados_focos[foco] = estado
        return jsonify({"respuesta": "Orden guardada"}), 200
    return jsonify({"respuesta": "Error"}), 400

@app.route('/update', methods=['POST'])
def actualizar_esp32():
    # El ESP32 avisa que está vivo y pregunta si debe prender algo
    datos = request.json
    nombre_dispositivo = datos.get('id_dispositivo', 'Desconocido')
    
    # Guardamos la hora de su última conexión
    dispositivos_en_linea[nombre_dispositivo] = datetime.now().strftime("%H:%M:%S")
    
    # Le regresamos al ESP32 los estados de los focos
    return jsonify(estados_focos), 200

if __name__ == '__main__':
    app.run(debug=True)