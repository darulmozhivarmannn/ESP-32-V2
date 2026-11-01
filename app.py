import os
import base64
from flask import Flask, request, jsonify
from anthropic import Anthropic

app = Flask(__name__)

# Initialize Anthropic client using environment variable ANTHROPIC_API_KEY
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

@app.route('/', methods=['GET'])
def index():
    return "ESP32-S3 AI Camera Backend is running!", 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get raw binary image from POST request body
        image_bytes = request.data
        if not image_bytes:
            return jsonify({"error": "No image data provided"}), 400

        # Encode image to base64 for Claude Vision API
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Send request to Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": "Describe what you see briefly for a small 0.96 inch OLED screen display. Keep it under 20 words, clean text only."
                        }
                    ]
                }
            ]
        )

        result_text = response.content[0].text.strip()
        return jsonify({"result": result_text}), 200

    except Exception as e:
        print(f"Error processing image: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
