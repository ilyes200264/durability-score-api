"""
Durability Score API
---------------------

Author: Ilyes Ghorieb
Description:
    This is a lightweight Flask API to evaluate the sustainability score of physical products
    based on their materials, weight, transport method, and packaging.

    It includes three main endpoints:
    - POST /score: Calculate a sustainability score and return suggestions
    - GET /history: View all previous assessments stored in the database
    - GET /score-summary: Get statistics on all assessments

Technologies:
    - Flask
    - SQLite via SQLAlchemy ORM
    - Swagger (via flasgger) for documentation

Last updated: April 2025
"""


from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
from collections import Counter, OrderedDict
import json
import os

app = Flask(__name__)
swagger = Swagger(app)


# Configuration de la base SQLite avec SQLAlchemy
app.config.from_mapping(
    SQLALCHEMY_DATABASE_URI='sqlite:///history.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)

db = SQLAlchemy(app)    # Connexion entre Flask et la base de données via SQLAlchemy


class Submission(db.Model):
    # Modèle représentant une soumission avec les champs stockés dans la base SQLite
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100))
    sustainability_score = db.Column(db.Float)
    rating = db.Column(db.String(2))
    suggestions = db.Column(db.Text)


# Vérifie que toutes les données requises sont présentes et du bon type
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
    """
    Calculate sustainability score
    ---
    tags:
      - Scoring
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            product_name:
              type: string
              example: "Reusable Bottle"
            materials:
              type: array
              items:
                type: string
              example: ["aluminum", "plastic"]
            weight_grams:
              type: number
              example: 300
            transport:
              type: string
              example: "air"
            packaging:
              type: string
              example: "recyclable"
    responses:
      200:
        description: Sustainability score calculated
    """
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
    
    # Logique de calcul du score de durabilité selon les critères
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

    
    # Enregistrement de la soumission dans la base de données
    entry = Submission(
        product_name=product_name,
        sustainability_score=round(score, 2),
        rating=rating,
        suggestions=json.dumps(suggestions)
    )
    db.session.add(entry)
    db.session.commit()

    response = OrderedDict()
    response["product_name"] = product_name
    response["sustainability_score"] = round(score, 2)
    response["rating"] = rating
    response["suggestions"] = suggestions

    return Response(json.dumps(response), mimetype='application/json')

@app.route('/history', methods=['GET'])
def get_history():
    """
    Get the history of submissions
    ---
    tags:
      - History
    responses:
      200:
        description: List of previous sustainability assessments
    """
    entries = Submission.query.all()
    result = []
    for entry in entries:
        item = OrderedDict()
        item["product_name"] = entry.product_name
        item["sustainability_score"] = entry.sustainability_score
        item["rating"] = entry.rating
        item["suggestions"] = json.loads(entry.suggestions)
        result.append(item)
    return Response(json.dumps(result), mimetype='application/json')

@app.route('/score-summary', methods=['GET'])
def score_summary():
    """
    Get summary statistics about sustainability scores
    ---
    tags:
      - Summary
    responses:
      200:
        description: Score statistics and top issues
    """
    entries = Submission.query.all()
    if not entries:
        response = OrderedDict()
        response["total_products"] = 0
        response["average_score"] = 0
        response["ratings"] = {"A": 0, "B": 0, "C": 0, "D": 0}
        response["top_issues"] = []
        return Response(json.dumps(response), mimetype='application/json')

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

    response = OrderedDict()
    response["total_products"] = total
    response["average_score"] = average_score
    response["ratings"] = ratings_counter
    response["top_issues"] = top_issues

    return Response(json.dumps(response), mimetype='application/json')

if __name__ == '__main__':
    if not os.path.exists("instance"):
        os.makedirs("instance")

    if not os.path.exists("instance/history.db"):
        with app.app_context():
            db.create_all()

    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
