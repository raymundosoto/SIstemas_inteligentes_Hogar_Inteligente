# Se agregaron 'redirect' y 'url_for' a la importación
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Diccionario maestro de agentes
agentes = {}

@app.route('/')
def index():
    """Ruta principal del Dashboard."""
    return render_template('index.html', agentes=agentes)

@app.route('/update', methods=['POST'])
def update_status():
    datos = request.json
    if not datos:
        return jsonify({"status": "error", "message": "No se recibieron datos"}), 400
    
    id_esp = datos.get('id_dispositivo', 'Agente_Anonimo')
    hora_actual = datetime.now().strftime("%H:%M:%S")

    agentes[id_esp] = {
        "nombre": id_esp,
        "hora": hora_actual,
        "temp": datos.get('temp', 0),
        "hum": datos.get('hum', 0),
        "viento": datos.get('viento', 0),
        "act1": int(datos.get('act1', 0)),
        "act2": int(datos.get('act2', 0)),
        "act3": int(datos.get('act3', 0))
    }
    return jsonify({"status": "recibido", "agente": id_esp}), 200

# RUTA PARA BORRAR AGENTES (Corregida)
@app.route('/borrar/<id_agente>')
def borrar_agente(id_agente):
    # Usamos pop con un valor por defecto para evitar errores si el ID no existe
    agentes.pop(id_agente, None) 
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)