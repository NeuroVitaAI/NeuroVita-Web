from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("La variable de entorno OPENROUTER_API_KEY no está definida.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/preguntar", methods=["POST"])
def preguntar():
    try:
        data = request.json
        user_message = data.get("mensaje", "")
        if not user_message:
            return jsonify({"respuesta": "❌ No has escrito ningún mensaje."})

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "Eres NeuroVita AI, una IA experta en negocios, salud mental y redes."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response_json = response.json()

        print("Respuesta API completa:", response_json)

        if response.status_code != 200:
            error_msg = response_json.get('error', {}).get('message') or response_json.get('message') or 'Error desconocido'
            return jsonify({"respuesta": f"❌ Error en la API: {error_msg}"})

        choices = response_json.get("choices")
        if not choices or not isinstance(choices, list):
            return jsonify({"respuesta": "❌ La API no devolvió resultados válidos."})

        respuesta = choices[0].get("message", {}).get("content", "")
        if not respuesta:
            return jsonify({"respuesta": "❌ La API devolvió una respuesta vacía."})

        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("❌ Error en preguntar:", e)
        return jsonify({"respuesta": f"❌ Error al procesar la solicitud: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)

