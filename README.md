# Durability Score API

This is a lightweight Flask API that calculates a **sustainability score** for physical products based on materials, weight, transport method, and packaging. It uses SQLite to store the history of submissions.

---

## 🔧 Endpoints

### GET `/`
Basic welcome route to verify that the API is running.

**Response**

Bienvenue sur l'API de durabilité !

### `POST /score`

**Request:**
```json
{
  "product_name": "Reusable Bottle", 
  "materials": ["aluminum", "plastic"],
  "weight_grams": 300,
  "transport": "air",
  "packaging": "recyclable"
}
```
Response:
```json
{
    "product_name": "Reusable Bottle",
    "sustainability_score": 90,
    "rating": "A",
    "suggestions": ["Avoid using plastic", "Consider using recycled aluminum", "Avoid air transport"]
}
```
### GET /history
Returns a list of previously submitted products with their score, rating, and suggestions.

### GET /score-summary
Returns a statistical summary of all submitted scores, including:

Average score

Highest and lowest score

Distribution of ratings

Example Response:
```json
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
```
# Installation

git clone https://github.com/ilyes200264/durability-score-api.git

cd durability-score-api

python -m venv venv

# Activate the virtual environment

# On macOS/Linux:

source venv/bin/activate

# On Windows:
Check first if you are on the right directory or not, then open the powershell and enter the commands below :

venv\Scripts\activate

pip install -r requirements.txt

python app.py

The API will be running at: http://localhost:5000

# Unit Testing

pytest
Tests are included in the test_app.py file and cover both the API routes and business logic.

🗃️ Technical Notes
SQLite database is located at instance/history.db

.gitignore excludes the venv/ and __pycache__/ folders

The codebase is intentionally simple and clear for case study purposes
