from flask import Flask, request, jsonify, render_template
from qa_system import get_answer_from_url  # Import the function from your existing code

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Make sure index.html is in the same folder

@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = request.get_json()
    url = data.get("url")
    question = data.get("question")

    if not url or not question:
        return jsonify({"answer": "Missing URL or question!"})

    output_path = "web_content.txt"  # Store scraped content temporarily
    answer = get_answer_from_url(url, question, output_path)
    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
