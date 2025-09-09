# main.py
import os
from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Error al inicializar el cliente de OpenAI: {e}")
    client = None

@app.route('/solicitar', methods=['POST'])
def solicitar_asistencia():
    if not client:
        return jsonify({"error": "El cliente de OpenAI no está inicializado. Revisa la API key."}), 500

    data = request.get_json()
    if not data or 'instrucciones' not in data or 'pregunta' not in data:
        return jsonify({"error": "La petición debe incluir 'instrucciones' y 'pregunta'."}), 400

    instrucciones = data.get('instrucciones')
    pregunta = data.get('pregunta')

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": instrucciones},
                {"role": "user", "content": pregunta}
            ]
        )
        respuesta_ia = completion.choices[0].message.content
        return respuesta_ia

    except Exception as e:
        return jsonify({"error": f"Error al contactar la API de OpenAI: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)