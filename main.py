# from fastapi import FastAPI, Header, HTTPException
# from pydantic import BaseModel
# from typing import List, Optional
# import re
# import os

# app = FastAPI()
# @app.get("/")
# def root():
#     return {
#         "status": "running",
#         "service": "Scam Honeypot API",
#         "docs": "/docs"
#     }

# API_KEY = os.getenv("API_KEY", "test_key_123")

# session_store = {}
# intelligence_store = {}


# class Message(BaseModel):
#     sender: str
#     text: str
#     timestamp: str


# class ConversationItem(BaseModel):
#     sender: str
#     text: str
#     timestamp: str


# class Metadata(BaseModel):
#     channel: Optional[str] = None
#     language: Optional[str] = None
#     locale: Optional[str] = None


# class IncomingRequest(BaseModel):
#     sessionId: str
#     message: Message
#     conversationHistory: List[ConversationItem] = []
#     metadata: Optional[Metadata] = None
# def normalize_text(text: str) -> str:
#     text = text.lower()

#     replacements = {
#         " ": "",
#         "[dot]": ".",
#         "(dot)": ".",
#         "{dot}": ".",
#         "[.]": ".",
#         "hxxp://": "http://",
#         "hxxps://": "https://",
#         "at": "@"
#     }

#     for key, value in replacements.items():
#         text = text.replace(key, value)

#     return text

# def is_scam_message(text: str) -> bool:
#     scam_keywords = [
#         "blocked",
#         "verify",
#         "urgent",
#         "account",
#         "upi",
#         "bank",
#         "click",
#         "suspend",
#         "immediately"
#     ]

#     text_lower = text.lower()
#     for word in scam_keywords:
#         if word in text_lower:
#             return True

#     return False

# def extract_upi_ids(text: str):
#     return re.findall(r'[\w.\-]+@[\w]+', text)

# def extract_urls(text: str):
#     return re.findall(r'https?://\S+', text)

# def extract_phone_numbers(text: str):
#     return re.findall(r'\+91\d{10}', text)

# def extract_suspicious_keywords(text: str):
#     keywords = ["urgent", "verify", "blocked", "account", "upi", "bank", "immediately"]
#     found = []
#     text_lower = text.lower()
#     for k in keywords:
#         if k in text_lower:
#             found.append(k)
#     return found


# @app.post("/api/message")
# def handle_message(
#     data: IncomingRequest,
#     x_api_key: str = Header(None)
# ):
#     if x_api_key != API_KEY:
#         raise HTTPException(status_code=401, detail="Invalid API key")

#     session_id = data.sessionId
#     incoming_text = normalize_text(data.message.text)


#     # Initialize stores
#     if session_id not in session_store:
#         session_store[session_id] = []

#     if session_id not in intelligence_store:
#         intelligence_store[session_id] = {
#             "upiIds": [],
#             "phishingLinks": [],
#             "phoneNumbers": [],
#             "suspiciousKeywords": []
#         }

#     # Save incoming message
#     session_store[session_id].append({
#         "sender": data.message.sender,
#         "text": incoming_text,
#         "timestamp": data.message.timestamp
#     })

#     #  EXTRACT INTELLIGENCE
#     intelligence_store[session_id]["upiIds"].extend(
#         extract_upi_ids(incoming_text)
#     )
#     intelligence_store[session_id]["phishingLinks"].extend(
#         extract_urls(incoming_text)
#     )
#     intelligence_store[session_id]["phoneNumbers"].extend(
#         extract_phone_numbers(incoming_text)
#     )
#     intelligence_store[session_id]["suspiciousKeywords"].extend(
#         extract_suspicious_keywords(incoming_text)
#     )

#     scam_detected = is_scam_message(incoming_text)
#     turn_count = len(session_store[session_id])

#     #  Multi-turn agent logic
#     if scam_detected:
#         if turn_count == 1:
#             reply_text = "Why is my account being blocked? I did not receive any notice."
#         elif turn_count == 2:
#             reply_text = "Which bank are you calling from? I need confirmation."
#         elif turn_count == 3:
#             reply_text = "I already updated my KYC last month. What is the issue now?"
#         else:
#             reply_text = "Can you explain the process again? I am confused."
#     else:
#         reply_text = "Okay, noted."

#     # Save agent reply
#     session_store[session_id].append({
#         "sender": "user",
#         "text": reply_text,
#         "timestamp": data.message.timestamp
#     })

#     # Deduplicate extracted intelligence (Member 3 task)
#     for key in intelligence_store[session_id]:
#       intelligence_store[session_id][key] = list(
#         set(intelligence_store[session_id][key])
#     )


#     return {
#     "scamDetection": {
#         "isScam": scam_detected,
#         "confidenceScore": 0.9 if scam_detected else 0.2
#     },
#     "engagement": {
#         "turnCount": turn_count,
#         "reply": reply_text
#     },
#     "extractedIntelligence": intelligence_store[session_id]
#     }



from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import re
import os
import uuid
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "AI Scam Honeypot API",
        "docs": "/docs"
    }

API_KEY = os.getenv("API_KEY", "test_key_123")

session_store = {}
intelligence_store = {}
risk_store = {}

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
    sessionId: Optional[str] = None
    message: Message
    conversationHistory: List[ConversationItem] = []
    metadata: Optional[Metadata] = None

def normalize_text(text: str) -> str:
    text = text.lower()

    replacements = {
        "[dot]": ".",
        "(dot)": ".",
        "{dot}": ".",
        "[.]": ".",
        "hxxp://": "http://",
        "hxxps://": "https://",
        "(at)": "@"
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


def extract_upi_ids(text: str):
    return re.findall(r'[\w.\-]+@[\w]+', text)

def extract_urls(text: str):
    return re.findall(r'https?://[^\s]+', text)

def extract_phone_numbers(text: str):
    return re.findall(r'\+91\d{10}', text)

def extract_keywords(text: str):
    keywords = [
        "urgent","verify","blocked","account","bank",
        "upi","click","suspend","immediately","kyc","refund"
    ]
    return [k for k in keywords if k in text]

def analyze_scam(text: str):
    score = 0
    reasons = []

    if extract_keywords(text):
        score += len(extract_keywords(text))
        reasons.append("suspicious_keywords")

    if any(w in text for w in ["urgent","immediately","now"]):
        score += 2
        reasons.append("urgency_language")

    if extract_urls(text):
        score += 3
        reasons.append("phishing_link")

    if extract_upi_ids(text):
        score += 4
        reasons.append("upi_payment_request")

    if extract_phone_numbers(text):
        score += 3
        reasons.append("phone_number_present")

    if len(reasons) >= 2:
        score += 2
        reasons.append("multi_signal_correlation")

    confidence = min(score / 10, 1.0)

    if confidence >= 0.75:
        severity = "HIGH"
    elif confidence >= 0.45:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return {
        "isScam": confidence >= 0.5,
        "confidenceScore": round(confidence, 2),
        "severity": severity,
        "reasons": reasons
    }

def apply_safety_governor(agent_reply: str, total_messages: int):
    banned_terms = ["pay", "send", "transfer", "upi", "money"]

    safe_reply = agent_reply
    for term in banned_terms:
        safe_reply = safe_reply.replace(term, "")

    if total_messages >= 5:
        return "I am not comfortable continuing this conversation. Please contact official support."

    return safe_reply.strip()

def send_final_guvi_callback(session_id: str, final_payload: dict):
    callback_payload = {
        "sessionId": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "result": final_payload
    }
    return {
        "status": "prepared",
        "targetEndpoint": "https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
        "payload": callback_payload
    }

@app.post("/api/message")
def handle_message(data: IncomingRequest, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    session_id = data.sessionId or str(uuid.uuid4())
    incoming_text = normalize_text(data.message.text)

    if session_id not in session_store:
        session_store[session_id] = []
        intelligence_store[session_id] = {
            "upiIds": [],
            "phishingLinks": [],
            "phoneNumbers": [],
            "keywords": []
        }
        risk_store[session_id] = {
            "createdAt": datetime.utcnow().isoformat(),
            "messages": 0,
            "riskTrend": []
        }

    session_store[session_id].append({
        "sender": data.message.sender,
        "text": incoming_text,
        "timestamp": data.message.timestamp
    })

    intelligence_store[session_id]["upiIds"].extend(extract_upi_ids(incoming_text))
    intelligence_store[session_id]["phishingLinks"].extend(extract_urls(incoming_text))
    intelligence_store[session_id]["phoneNumbers"].extend(extract_phone_numbers(incoming_text))
    intelligence_store[session_id]["keywords"].extend(extract_keywords(incoming_text))

    for k in intelligence_store[session_id]:
        intelligence_store[session_id][k] = list(set(intelligence_store[session_id][k]))

    scam_result = analyze_scam(incoming_text)
    risk_store[session_id]["messages"] += 1
    risk_store[session_id]["riskTrend"].append(scam_result["confidenceScore"])

    turn_count = len(session_store[session_id])

    if scam_result["isScam"]:
        replies = [
            "Why is my account being blocked?",
            "Which bank are you calling from?",
            "I already completed KYC last month.",
            "Please explain the issue clearly.",
            "I will check and get back to you."
        ]
        agent_reply = replies[min(turn_count - 1, len(replies) - 1)]
    else:
        agent_reply = "Okay."

    reply_text = apply_safety_governor(agent_reply, turn_count)

    session_store[session_id].append({
        "sender": "user",
        "text": reply_text,
        "timestamp": data.message.timestamp
    })

    return {
        "sessionId": session_id,
        "scamDetection": scam_result,
        "engagement": {
            "turnCount": turn_count,
            "reply": reply_text
        },
        "extractedIntelligence": intelligence_store[session_id],
        "sessionRisk": risk_store[session_id]
    }

@app.get("/api/session/{session_id}")
def get_session(session_id: str, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    if session_id not in session_store:
        raise HTTPException(status_code=404, detail="Session not found")

    final_callback_preview = send_final_guvi_callback(
        session_id,
        {
            "conversation": session_store[session_id],
            "intelligence": intelligence_store[session_id],
            "risk": risk_store[session_id]
        }
    )

    return {
        "sessionId": session_id,
        "conversation": session_store[session_id],
        "intelligence": intelligence_store[session_id],
        "risk": risk_store[session_id],
        "guviFinalCallbackReady": final_callback_preview
    }
