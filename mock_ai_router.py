from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.get_json()
    # We ignore the input and return a fixed response
    response = {
        "choices": [{
            "message": {
                "content": '{"title": "Mock Title", "caption": "Mock Caption", "hashtags": "#mock #test", "cta": "Follow!", "image_prompt": "A mock image"}'
            }
        }]
    }
    return jsonify(response)

@app.route('/v1/images/generations', methods=['POST'])
def image_generations():
    # Return a placeholder image URL
    response = {
        "data": [{
            "url": "https://via.placeholder.com/1024"
        }]
    }
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='localhost', port=20128, debug=False)