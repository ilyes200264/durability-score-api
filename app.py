from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from collections import Counter
import json
import os

app = Flask(__name__)
app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI='sqlite:///history.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    sustainability_score = db.Column(db.Float)
    rating = db.Column(db.String(2))
    suggestions = db.Column(db.Text)

def validate_input(data):
    required_fields = {
        "product_name": str,
        "materials": list,
        "weight_grams": (int, float),
        "transport": str,
        "packaging": str
    }

    for field, expected_type in required_fields.items():
        if field not in data:
            return f"'{field}' is required"
        if not isinstance(data[field], expected_type):
            return f"'{field}' must be of type {expected_type}"

    allowed_transports = ["air", "rail", "sea", "road"]
    if data["transport"] not in allowed_transports:
        return f"'transport' must be one of {allowed_transports}"

    allowed_packaging = ["recyclable", "biodegradable", "non-recyclable"]
    if data["packaging"] not in allowed_packaging:
        return f"'packaging' must be one of {allowed_packaging}"

    return None

@app.route('/')
def home():
    return "Bienvenue sur l'API de durabilité !"

@app.route('/score', methods=['POST'])
def score():
    data = request.get_json()

    error = validate_input(data)
    if error:
        return jsonify({"error": error}), 400

    product_name = data["product_name"]
    materials = data["materials"]
    weight_grams = data["weight_grams"]
    transport = data["transport"]
    packaging = data["packaging"]

    score = 100
    suggestions = []

    if "plastic" in materials:
        score -= 10
        suggestions.append("Avoid using plastic")

    if "recycled" in materials:
        score += 10

    if "aluminum" in materials:
        score += 5
        if "recycled" not in materials:
            suggestions.append("Consider using recycled aluminum")

    if transport == "air":
        score -= 15
        suggestions.append("Avoid air transport")
    elif transport in ["rail", "sea"]:
        score += 5

    if packaging in ["recyclable", "biodegradable"]:
        score += 10
    else:
        suggestions.append("Use recyclable or biodegradable packaging")

    if weight_grams > 500:
        score -= 5
        suggestions.append("Reduce product weight")

    if score >= 90:
        rating = "A"
    elif score >= 75:
        rating = "B"
    elif score >= 60:
        rating = "C"
    else:
        rating = "D"

    entry = Submission(
        product_name=product_name,
        sustainability_score=round(score, 2),
        rating=rating,
        suggestions=json.dumps(suggestions)
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        "product_name": product_name,
        "sustainability_score": round(score, 2),
        "rating": rating,
        "suggestions": suggestions
    })

@app.route('/history', methods=['GET'])
def get_history():
    entries = Submission.query.all()
    result = []
    for entry in entries:
        result.append({
            "product_name": entry.product_name,
            "sustainability_score": entry.sustainability_score,
            "rating": entry.rating,
            "suggestions": json.loads(entry.suggestions)
        })
    return jsonify(result)

@app.route('/score-summary', methods=['GET'])
def score_summary():
    entries = Submission.query.all()
    if not entries:
        return jsonify({
            "total_products": 0,
            "average_score": 0,
            "ratings": {"A": 0, "B": 0, "C": 0, "D": 0},
            "top_issues": []
        })

    total = len(entries)
    total_score = sum(e.sustainability_score for e in entries)
    average_score = round(total_score / total, 2)

    ratings_counter = {"A": 0, "B": 0, "C": 0, "D": 0}
    issues_list = []

    for e in entries:
        if e.rating in ratings_counter:
            ratings_counter[e.rating] += 1
        issues_list.extend(json.loads(e.suggestions))

    top_issues = [issue for issue, _ in Counter(issues_list).most_common(3)]

    return jsonify({
        "total_products": total,
        "average_score": average_score,
        "ratings": ratings_counter,
        "top_issues": top_issues
    })

if __name__ == '__main__':
    if not os.path.exists("instance"):
        os.makedirs("instance")

    if not os.path.exists("instance/history.db"):
        with app.app_context():
            db.create_all()

    app.run(debug=True)
