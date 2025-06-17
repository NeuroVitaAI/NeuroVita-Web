from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)

# 🔧 Corrección: quitar paréntesis y usar correctamente el valor por defecto
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

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
            "model": "mistralai/mistral-7b-instruct",  # Modelo gratuito
            "messages": [
                {"role": "system", "content": "Eres NeuroVita AI, una IA experta en negocios, salud mental y redes."},
                {"role": "user", "content": user_message}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        respuesta = response.json()["choices"][0]["message"]["content"]

        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"respuesta": f"❌ Error al procesar la solicitud: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
