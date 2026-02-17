from fastapi import FastAPI, File, UploadFile
import pytesseract
import pdfplumber
from PIL import Image
import shutil
import os

# Connect Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_pdf_text(path):
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_image_text(path):
    image = Image.open(path)
    text = pytesseract.image_to_string(image)
    return text

def analyze_text(text):
    suggestions = []

    word_count = len(text.split())

    if word_count < 20:
        suggestions.append("Content is too short. Add more value to engage users.")

    if word_count > 250:
        suggestions.append("Content is too long. Shorter posts usually perform better.")

    if "#" not in text:
        suggestions.append("Add relevant hashtags to improve discoverability.")

    if "?" not in text:
        suggestions.append("Ask a question to encourage audience interaction.")

    if "!" not in text:
        suggestions.append("Consider adding a strong call-to-action.")

    if len(text.strip()) == 0:
        suggestions.append("No readable text detected. Please upload a clearer file.")

    if not suggestions:
        suggestions.append("Content looks engaging. Minor tweaks could further optimize reach.")

    return suggestions

@app.get("/")
def home():
    return {"message": "Social Media Analyzer Running"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not file:
        return {"error": "No file uploaded"}

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.content_type == "application/pdf":
            text = extract_pdf_text(file_path)
        elif file.content_type.startswith("image/"):
            text = extract_image_text(file_path)
        else:
            return {"error": "Unsupported file type"}

        suggestions = analyze_text(text)

        return {
            "extracted_text": text,
            "suggestions": suggestions
        }

    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)






