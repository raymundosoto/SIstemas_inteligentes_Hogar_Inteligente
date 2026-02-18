from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Diccionario maestro para almacenar la información de cada agente
# Estructura: {"Nombre_Agente": {"hora": "...", "temp": 0, "act1": 0, ...}}
agentes = {}

@app.route('/')
def index():
    """Ruta principal que renderiza el Dashboard con todos los agentes."""
    return render_template('index.html', agentes=agentes)

@app.route('/update', methods=['POST'])
def update_status():
    """
    Ruta que recibe los datos desde el ESP32-C3.
    Une el ID del dispositivo con sus variables y estados en un solo objeto.
    """
    datos = request.json
    
    # Validamos que lleguen datos básicos
    if not datos:
        return jsonify({"status": "error", "message": "No se recibieron datos"}), 400
    
    # Extraemos el ID del dispositivo para identificar al agente
    id_esp = datos.get('id_dispositivo', 'Agente_Anonimo')
    
    # Obtenemos la hora actual del servidor para el registro de sincronización
    hora_actual = datetime.now().strftime("%H:%M:%S")

    # Guardamos o actualizamos TODA la información en un solo contenedor por ID
    agentes[id_esp] = {
        "nombre": id_esp,
        "hora": hora_actual,
        "temp": datos.get('temp', 0),
        "hum": datos.get('hum', 0),
        "viento": datos.get('viento', 0),
        "act1": int(datos.get('act1', 0)), # Ventilador
        "act2": int(datos.get('act2', 0)), # Humidificador
        "act3": int(datos.get('act3', 0))  # Iluminación
    }
    
    print(f"Sincronización exitosa: {id_esp} a las {hora_actual}")
    return jsonify({"status": "recibido", "agente": id_esp}), 200

@app.route('/orden', methods=['POST'])
def recibir_orden():
    """Ruta para permitir el control manual remoto desde el Dashboard o CMD."""
    datos = request.json
    id_esp = datos.get('id_dispositivo')
    actuador = datos.get('led') # Se mantiene 'led' por compatibilidad con comandos previos
    estado = datos.get('estado')
    
    # Mapeo de 'led' a 'act' para consistencia interna
    mapeo = {"led1": "act1", "led2": "act2", "led3": "act3"}
    clave_act = mapeo.get(actuador)

    if id_esp in agentes and clave_act:
        agentes[id_esp][clave_act] = int(estado)
        return jsonify({"status": "ok", "mensaje": f"{actuador} actualizado"}), 200
    
    return jsonify({"status": "error", "message": "Agente no encontrado"}), 404

# NUEVA RUTA PARA BORRAR AGENTES
@app.route('/borrar/<id_agente>')
def borrar_agente(id_agente):
    if id_agente in agentes:
        agentes.pop(id_agente) # Elimina el agente del diccionario
    return redirect(url_for('index')) # Redirige al dashboard actualizado

if __name__ == '__main__':
    # Nota: En PythonAnywhere no se usa app.run(), 
    # se configura desde la pestaña Web.
    app.run(debug=True)