from fastapi import FastAPI, File, UploadFile
import pdfplumber
import re
from transformers import pipeline
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

app = FastAPI()

# Load summarizer (free HuggingFace model)
summarizer = pipeline("summarization", model="google/pegasus-xsum")

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def classify_and_extract(text):
    # Very naive classifier
    if re.search(r"(ID|Identity|Passport|Address|DOB)", text, re.I):
        return "id_card"
    elif len(text.split()) > 200:
        return "story"
    else:
        return "generic"
    
def ocr_extract_text(pdf_file):
    pages = convert_from_path(pdf_file)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page, lang="eng") + "\n"
    return text    

def extract_fields(doc_type, text):
    if doc_type == "id_card":
        name = re.search(r"Name[:\s]+([A-Za-z ]+)", text)
        id_no = re.search(r"(ID|Passport|No)[:\s]+([A-Z0-9]+)", text)
        address = re.search(r"Address[:\s]+(.+)", text)
        return {
            "Name": name.group(1) if name else None,
            "ID Number": id_no.group(2) if id_no else None,
            "Address": address.group(1) if address else None
        }
    elif doc_type == "story":
        summary = summarizer(text, max_length=30, min_length=2, do_sample=False)
        return {"Summary": summary[0]['summary_text']}
    else:
        # Generic summarization
        summary = summarizer(text, max_length=10, min_length=1, do_sample=False)
        return {"Gist": summary[0]['summary_text']}

@app.post("/analyze_pdf/")
async def analyze_pdf(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file.file)
    doc_type = classify_and_extract(text)
    data = extract_fields(doc_type, text)
    #data = ocr_extract_text(text)
    return {
        "doc_type": "Generic",
        "extracted_data": data
    }


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

# To run the server, use:
# uvicorn main:app --reload
