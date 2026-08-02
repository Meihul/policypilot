import os
import requests

from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.textanalytics import TextAnalyticsClient

load_dotenv()

# -----------------------------
# Document Intelligence
# -----------------------------

doc_client = DocumentIntelligenceClient(
    endpoint=os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("DOCUMENT_INTELLIGENCE_KEY"))
)

# -----------------------------
# Azure Language
# -----------------------------

language_client = TextAnalyticsClient(
    endpoint=os.getenv("LANGUAGE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("LANGUAGE_KEY"))
)

# -----------------------------
# Translator
# -----------------------------

translator_key = os.getenv("TRANSLATOR_KEY")
translator_endpoint = os.getenv("TRANSLATOR_ENDPOINT")
translator_region = os.getenv("TRANSLATOR_REGION")

def extract_text(pdf_path):

    with open(pdf_path, "rb") as f:

        poller = doc_client.begin_analyze_document(
            "prebuilt-layout",
            body=f
        )

    result = poller.result()

    text = ""

    for page in result.pages:
        for line in page.lines:
            text += line.content + "\n"

    return text

def analyze_text(text):

    documents = [text[:5000]]

    key_phrases = language_client.extract_key_phrases(documents)[0].key_phrases

    entities = language_client.recognize_entities(documents)[0].entities

    language = language_client.detect_language(documents)[0].primary_language.name

    filtered_entities = []

    ignored_categories = {
        "Quantity",
        "Number"
    }

    for e in entities:
        if e.category not in ignored_categories:
            filtered_entities.append({
                "text": e.text,
                "category": e.category
            })

    return {
        "language": language,
        "key_phrases": key_phrases[:20],   # Top 20 key phrases
        "entities": filtered_entities
    }

def translate_text(text, target_language):

    path = "/translate"

    params = {
        "api-version": "3.0",
        "to": target_language
    }

    headers = {
        "Ocp-Apim-Subscription-Key": translator_key,
        "Ocp-Apim-Subscription-Region": translator_region,
        "Content-type": "application/json"
    }

    body = [
        {
            "text": text[:4000]
        }
    ]

    response = requests.post(
        translator_endpoint + path,
        params=params,
        headers=headers,
        json=body
    )

    result = response.json()

    return result[0]["translations"][0]["text"]