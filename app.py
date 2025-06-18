from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def determinar_max_tokens(mensaje):
    mensaje = mensaje.lower()
    if any(saludo in mensaje for saludo in ["hola", "buenos días", "qué tal"]):
        return 100  # respuestas cortas para saludos
    elif "contenido viral" in mensaje or "ideas" in mensaje:
        return 600  # respuestas largas para temas complejos
    elif "negocios" in mensaje or "salud mental" in mensaje:
        return 400  # respuestas intermedias
    else:
        return 300  # respuesta estándar un poco más larga

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

        max_tokens = determinar_max_tokens(user_message)

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct",
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": "Eres NeuroVita AI, una IA experta en negocios, salud mental y redes."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response_json = response.json()

        if response.status_code != 200:
            return jsonify({"respuesta": f"❌ Error en la API: {response_json.get('error', 'Error desconocido')}"})

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
