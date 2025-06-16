from flask import Flask, request, jsonify, render_template
import openai


openai.api_key = "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"  
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/preguntar', methods=['POST'])
def preguntar():
    data = request.get_json()
    pregunta = data.get('mensaje', '')

    try:
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres NeuroVita AI, una IA avanzada que podrá hablar de cualquier tema, experta en contenido viral, negocios millonarios, viajes, salud mental y crecimiento personal."},
                {"role": "user", "content": pregunta}
            ]
        )
        texto = respuesta['choices'][0]['message']['content']
        return jsonify({"respuesta": texto.strip()})
    except Exception as e:
        return jsonify({"respuesta": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
