from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def determinar_tokens_y_prompt(mensaje):
    msg = mensaje.lower()
    max_tokens = 300
    temperature = 0.7
    system_msg = "Eres NeuroVita AI, una IA experta en negocios, salud mental y redes. Responde con claridad, estructura y de forma cercana, usando listas o puntos cuando sea útil."

    saludos = ["hola", "buenos días", "buenas tardes", "qué tal", "buen día", "saludos"]
    contenido_viral = ["contenido viral", "viral", "tiktok", "youtube", "ideas para contenido"]
    negocio = ["negocio", "emprender", "empresa", "marketing", "monetizar", "finanzas"]
    salud = ["salud mental", "estrés", "ansiedad", "bienestar", "psicología"]

    if any(greet in msg for greet in saludos):
        max_tokens = 170
        system_msg = "Eres NeuroVita AI, responde saludando de forma corta, clara y cercana."

    elif any(viral in msg for viral in contenido_viral):
        # Para preguntas muy cortas sobre viralidad, corta; para largas, larga.
        if len(msg.split()) < 5:
            max_tokens = 300
        else:
            max_tokens = 550
        system_msg = (
            "Eres NeuroVita AI, experto en contenido viral para redes sociales. "
            "Adapta la longitud de la respuesta según la pregunta: si el usuario pide consejos o ideas detalladas, da una respuesta larga y bien estructurada, "
            "pero si la pregunta es corta o simple, responde de forma más breve y directa. "
            "Usa listas y párrafos claros."
        )

    elif any(neg in msg for neg in negocio):
        max_tokens = 500
        system_msg = (
            "Eres NeuroVita AI, experto en negocios, marketing y finanzas. "
            "Adapta la longitud de la respuesta según la pregunta, da ejemplos prácticos y estructura la respuesta con claridad."
        )

    elif any(salud in msg for salud in salud):
        max_tokens = 400
        system_msg = (
            "Eres NeuroVita AI, experto en salud mental. Responde de forma empática, clara y con consejos útiles. "
            "Adapta la longitud según la pregunta."
        )
    else:
        # Por defecto respuesta clara, media
        max_tokens = 270
        system_msg = "Eres NeuroVita AI, una IA experta en negocios, salud mental y redes. Responde con claridad, estructura y de forma cercana."

    return max_tokens, temperature, system_msg

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/preguntar", methods=["POST"])
def preguntar():
    try:
        data = request.json
        user_message = data.get("mensaje", "").strip()
        if not user_message:
            return jsonify({"respuesta": "❌ No has escrito ningún mensaje."})

        max_tokens, temperature, system_message = determinar_tokens_y_prompt(user_message)

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        body = {
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response_json = response.json()

        if response.status_code != 200:
            error_msg = response_json.get("error") or response_json.get("message") or "Error desconocido"
            return jsonify({"respuesta": f"❌ Error en la API: {error_msg}"})

        choices = response_json.get("choices")
        if not choices or not isinstance(choices, list):
            return jsonify({"respuesta": "❌ La API no devolvió resultados válidos."})

        respuesta = choices[0].get("message", {}).get("content", "").strip()
        if not respuesta:
            return jsonify({"respuesta": "❌ La API devolvió una respuesta vacía."})

        return jsonify({"respuesta": respuesta})

    except Exception as e:
        print("❌ Error en preguntar:", e)
        return jsonify({"respuesta": f"❌ Error al procesar la solicitud: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
