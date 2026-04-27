import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model_flash = genai.GenerativeModel("gemini-1.5-flash")

def parse_expense_nl(text, group_members):
    try:
        prompt = f"""
        Extract the following details from this expense sentence: "{text}"
        Available Group Members: {', '.join(group_members)}
        Valid Categories: ["Food", "Transport", "Rent", "Groceries", "Entertainment", "Other"]
        Rules:
        1. 'paid_by' exact name from Available Group Members. 
        2. 'amount' float (total numeric amount paid).
        3. 'category' strictly one of the Valid Categories.
        4. 'description' brief summary.
        Return ONLY JSON format: {{"paid_by": "Raj", "amount": 840.0, "category": "Food", "description": "pizza"}}
        """
        response = model_flash.generate_content(prompt)
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except Exception as e:
        print(f"Error parsing NL with Gemini: {e}")
        return None

def extract_receipt(image_bytes, group_members):
    try:
        prompt = f"""
        You are a smart OCR assistant extracting a receipt.
        Identify the main total amount, a category (Food, Transport, Rent, Groceries, Entertainment, Other), and a short description.
        Available Group Members who might have paid: {', '.join(group_members)}
        Return ONLY JSON: {{"amount": 150.0, "category": "Food", "description": "McDonalds order"}}
        """
        response = model_flash.generate_content([{"mime_type": "image/jpeg", "data": image_bytes}, prompt])
        return json.loads(response.text.replace("```json", "").replace("```", "").strip())
    except Exception as e:
        print(f"Error parsing receipt with Gemini: {e}")
        return None

def generate_spending_roast(group_name, profiles_text):
    try:
        prompt = f"""
        You are an edgy, highly sarcastic AI financial advisor (think Wendy's Twitter meets a Wall Street banker).
        I have run a K-Means clustering algorithm on the recent expenses for the group '{group_name}'.
        Here are the personality profiles assigned to the members based on their math:
        
        {profiles_text}
        
        Write a very short (2-3 sentences), highly viral, absolutely ruthless but funny "spending roast" for the whole group based on this data. Don't use markdown or emojis unless making a point. Be witty!
        """
        response = model_flash.generate_content(prompt)
        return response.text
    except Exception as e:
        return "You're all too broke to even afford a proper AI roast right now."

