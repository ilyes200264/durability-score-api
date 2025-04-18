# Durability Score API

This is a lightweight Flask API that calculates a **sustainability score** for physical products based on materials, weight, transport method, and packaging. It uses SQLite to store the history of submissions.

---

## 🔧 Endpoints

### `POST /score`

**Request:**

{
  "product_name": "Reusable Bottle", 
  "materials": ["aluminum", "plastic"],
  "weight_grams": 300,
  "transport": "air",
  "packaging": "recyclable"
}

Response:

{
  "product_name": "Reusable Bottle",
  "sustainability_score": 72.5,
  "rating": "B",
  "suggestions": [
    "Avoid air transport",
    "Use biodegradable packaging"
  ]
}

GET /history
Returns a list of previously submitted products with their score, rating, and suggestions.

GET /score-summary
Returns a statistical summary of all submitted scores, including:

Average score

Highest and lowest score

Distribution of ratings

Example Response:

{
  "average_score": 68.2,
  "max_score": 92.0,
  "min_score": 45.0,
  "rating_counts": {
    "A": 3,
    "B": 5,
    "C": 2,
    "D": 1
  }
}

⚙️ Installation

git clone https://github.com/ilyes200264/durability-score-api.git

cd durability-score-api

python -m venv venv

# Activate the virtual environment

# On macOS/Linux:

source venv/bin/activate

# On Windows:
venv\Scripts\activate
pip install -r requirements.txt
python app.py
The API will be running at: http://localhost:5000

✅ Unit Testing

pytest
Tests are included in the test_app.py file and cover both the API routes and business logic.

🗃️ Technical Notes
SQLite database is located at instance/history.db

.gitignore excludes the venv/ and __pycache__/ folders

The codebase is intentionally simple and clear for case study purposes
