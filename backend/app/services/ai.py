
import json, os
from openai import OpenAI
from backend.app.schemas.item_schemas import GeneratedItem 
from pydantic import BaseModel
from docx import Document
from fastapi import APIRouter, HTTPException, Body
from dotenv import load_dotenv
from typing import Optional

router = APIRouter()
load_dotenv(dotenv_path = "./key.env")  # load .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# === 1. Define data type === 
class GenerateItemRequest(BaseModel):
    docx_path: Optional[str] = None
    prompt_text: Optional[str] = None 

# === 2. Read Word doc ===
def read_docx(path: str) -> str:
    """
    Read a .docx file and return all paragraphs joined as a string.
    """
    doc = Document(path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


# === 3. Route: generate items === 

def generate_item_from_prompt_text(prompt_text: str) -> dict:
    messages = [
    {"role": "system", "content": "You are an AI that generates exam items in JSON format."},
    {"role": "user", "content": prompt_text}]

    # Use OpenAI API
    response = client.chat.completions.create(
        model = "gpt-4o-mini",
        messages = messages,
        temperature=0.8,
        response_format = {"type":"json_object"}
    )
    raw = response.choices[0].message.content
  
  
    data = json.loads(raw)
 

    return data

def generate_item_from_prompt_request(r: GenerateItemRequest) -> dict:
    
    prompt = read_docx(r.docx_path) if r.docx_path else (r.prompt_text)
    return generate_item_from_prompt_text(prompt)