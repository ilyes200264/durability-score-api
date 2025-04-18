# Durability Score API

This is a lightweight Flask API that calculates a **sustainability score** for physical products based on materials, weight, transport method, and packaging. It uses SQLite to store the history of submissions.

# 📊 Scoring System (Starts at 100)

## ♻️ Conditions & Impacts

| Condition                                      | Score Impact | Suggestion Generated                              |
|------------------------------------------------|--------------|---------------------------------------------------|
| Contains `"plastic"` in materials              | -10          | ✅ Avoid using plastic                             |
| Contains `"recycled"` in materials             | +10          |                                                   |
| Contains `"aluminum"`                          | +5           |                                                   |
| `"aluminum"` but not `"recycled"`             | —            | ✅ Consider using recycled aluminum               |
| Transport is `"air"`                           | -15          | ✅ Avoid air transport                             |
| Transport is `"rail"` or `"sea"`               | +5           |                                                   |
| Packaging is `"recyclable"` or `"biodegradable"` | +10        |                                                   |
| Packaging is `"non-recyclable"`                | 0            | ✅ Use recyclable or biodegradable packaging       |
| Product weight exceeds 500 grams               | -5           | ✅ Reduce product weight                           |

---

## 🏅 Rating Thresholds

The final score is converted to a rating based on this scale:

| Score Range | Rating |
|-------------|--------|
| ≥ 90        | A      |
| 75 – 89     | B      |
| 60 – 74     | C      |
| < 60        | D      |


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
 "total_products": 12,
 "average_score": 68.3,
 "ratings": {
 "A": 2,
 "B": 5,
 "C": 4,
 "D": 1
 },
 "top_issues": [ "Plastic used", "Air transport", "Non-recyclable packaging"]
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
