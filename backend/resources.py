from pypdf import PdfReader
import json
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")

# Read LinkedIn PDF
try:
    linkedin_path = os.path.join(data_dir, "linkedin.pdf")
    reader = PdfReader(linkedin_path)
    linkedin = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            linkedin += text
except FileNotFoundError:
    linkedin = "LinkedIn profile not available"

# Read other data files
try:
    with open(os.path.join(data_dir, "summary.txt"), "r", encoding="utf-8") as f:
        summary = f.read()
except FileNotFoundError:
    summary = "Summary not available"

try:
    with open(os.path.join(data_dir, "style.txt"), "r", encoding="utf-8") as f:
        style = f.read()
except FileNotFoundError:
    style = "Style information not available"

try:
    with open(os.path.join(data_dir, "facts.json"), "r", encoding="utf-8") as f:
        facts = json.load(f)
except FileNotFoundError:
    facts = {
        "full_name": "Digital Twin",
        "name": "Assistant",
        "current_role": "AI Assistant",
        "location": "Unknown",
        "email": "not-available@example.com",
        "linkedin": "not-available",
        "specialties": ["AI", "Assistance"],
        "years_experience": 0,
        "education": []
    }