from flask import Flask, request, jsonify, render_template
from qa_system import get_answer_from_url  #  Correct import

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_answer', methods=['POST'])
def get_answer():
    try:
        data = request.json
        url = data.get("url")
        question = data.get("question")

        if not url or not question:
            return jsonify({"answer": "❌ URL and question are required."})

        # ✅ Use get_answer_from_url directly
        answer = get_answer_from_url(url, question)

        return jsonify({"answer": answer})

    except Exception as e:
        print(f"❌ Error in processing request: {str(e)}")
        return jsonify({"answer": "❌ Error fetching answer."})

if __name__ == '__main__':
    app.run(debug=True)
