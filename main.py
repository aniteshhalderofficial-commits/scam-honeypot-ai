from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import re
import os

app = FastAPI()

API_KEY = os.getenv("API_KEY", "test_key_123")

session_store = {}
intelligence_store = {}


class Message(BaseModel):
    sender: str
    text: str
    timestamp: str


class ConversationItem(BaseModel):
    sender: str
    text: str
    timestamp: str


class Metadata(BaseModel):
    channel: Optional[str] = None
    language: Optional[str] = None
    locale: Optional[str] = None


class IncomingRequest(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: List[ConversationItem] = []
    metadata: Optional[Metadata] = None

def is_scam_message(text: str) -> bool:
    scam_keywords = [
        "blocked",
        "verify",
        "urgent",
        "account",
        "upi",
        "bank",
        "click",
        "suspend",
        "immediately"
    ]

    text_lower = text.lower()
    for word in scam_keywords:
        if word in text_lower:
            return True

    return False

def extract_upi_ids(text: str):
    return re.findall(r'[\w.\-]+@[\w]+', text)

def extract_urls(text: str):
    return re.findall(r'https?://\S+', text)

def extract_phone_numbers(text: str):
    return re.findall(r'\+91\d{10}', text)

def extract_suspicious_keywords(text: str):
    keywords = ["urgent", "verify", "blocked", "account", "upi", "bank", "immediately"]
    found = []
    text_lower = text.lower()
    for k in keywords:
        if k in text_lower:
            found.append(k)
    return found


@app.post("/api/message")
def handle_message(
    data: IncomingRequest,
    x_api_key: str = Header(None)
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    session_id = data.sessionId
    incoming_text = data.message.text

    # Initialize stores
    if session_id not in session_store:
        session_store[session_id] = []

    if session_id not in intelligence_store:
        intelligence_store[session_id] = {
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "suspiciousKeywords": []
        }

    # Save incoming message
    session_store[session_id].append({
        "sender": data.message.sender,
        "text": incoming_text,
        "timestamp": data.message.timestamp
    })

    #  EXTRACT INTELLIGENCE
    intelligence_store[session_id]["upiIds"].extend(
        extract_upi_ids(incoming_text)
    )
    intelligence_store[session_id]["phishingLinks"].extend(
        extract_urls(incoming_text)
    )
    intelligence_store[session_id]["phoneNumbers"].extend(
        extract_phone_numbers(incoming_text)
    )
    intelligence_store[session_id]["suspiciousKeywords"].extend(
        extract_suspicious_keywords(incoming_text)
    )

    scam_detected = is_scam_message(incoming_text)
    turn_count = len(session_store[session_id])

    #  Multi-turn agent logic
    if scam_detected:
        if turn_count == 1:
            reply_text = "Why is my account being blocked? I did not receive any notice."
        elif turn_count == 2:
            reply_text = "Which bank are you calling from? I need confirmation."
        elif turn_count == 3:
            reply_text = "I already updated my KYC last month. What is the issue now?"
        else:
            reply_text = "Can you explain the process again? I am confused."
    else:
        reply_text = "Okay, noted."

    # Save agent reply
    session_store[session_id].append({
        "sender": "user",
        "text": reply_text,
        "timestamp": data.message.timestamp
    })

    # Deduplicate extracted intelligence (Member 3 task)
    for key in intelligence_store[session_id]:
      intelligence_store[session_id][key] = list(
        set(intelligence_store[session_id][key])
    )


    return {
    "scamDetection": {
        "isScam": scam_detected,
        "confidenceScore": 0.9 if scam_detected else 0.2
    },
    "engagement": {
        "turnCount": turn_count,
        "reply": reply_text
    },
    "extractedIntelligence": intelligence_store[session_id]
    }

