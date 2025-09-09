# main.py (Versión para Asistentes de OpenAI)
import os
import time
from flask import Flask, request, jsonify
from openai import OpenAI

# Inicializar Flask
app = Flask(__name__)

# Configurar el cliente de OpenAI y obtener el ID del Asistente desde las variables de entorno
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    ASSISTANT_ID = os.environ.get("OPENAI_ASSISTANT_ID")
except Exception as e:
    print(f"Error en la configuración inicial: {e}")
    client = None
    ASSISTANT_ID = None

@app.route('/solicitar', methods=['POST'])
def solicitar_asistencia():
    if not client or not ASSISTANT_ID:
        return jsonify({"error": "OpenAI no está configurado. Revisa la API Key y el Assistant ID."}), 500

    data = request.get_json()
    if not data or 'pregunta' not in data:
        # Nota: Ya no necesitamos las 'instrucciones', porque el Asistente ya las tiene.
        return jsonify({"error": "La petición debe incluir una 'pregunta'."}), 400

    pregunta_usuario = data.get('pregunta')

    try:
        # Paso 1: Crear un "Thread". Un Thread es como una nueva conversación.
        thread = client.beta.threads.create()

        # Paso 2: Añadir el mensaje del usuario a esa conversación (Thread).
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=pregunta_usuario
        )

        # Paso 3: Ejecutar el Asistente sobre esa conversación.
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
        )

        # Paso 4: Esperar a que el Asistente termine de pensar y generar la respuesta.
        while run.status != "completed":
            time.sleep(0.5) # Esperar medio segundo antes de volver a preguntar
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            # Manejar el caso de que el run falle
            if run.status == "failed":
                return jsonify({"error": "La ejecución del Asistente ha fallado."}), 500

        # Paso 5: Obtener todos los mensajes de la conversación.
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        # El primer mensaje [0] suele ser la respuesta del asistente.
        respuesta_ia = messages.data[0].content[0].text.value
        return respuesta_ia

    except Exception as e:
        return jsonify({"error": f"Ha ocurrido un error con la API de OpenAI: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)