# AI Agentic Scam Honeypot 

An AI-powered **agentic honeypot system** designed to detect, engage, and extract intelligence from scam messages (SMS, email, chat).  
The system simulates a real user, engages scammers in **multi-turn conversations**, and automatically extracts actionable scam indicators.

---

## Features

- **Scam Detection**
  - Keyword-based scam identification
  - Confidence scoring

- **Multi-Turn Agent Engagement**
  - Context-aware replies
  - Session-based conversation memory

- **Intelligence Extraction**
  - UPI IDs
  - Phishing URLs
  - Phone numbers
  - Suspicious keywords

- **Session Memory**
  - Tracks turn count per session
  - Maintains conversation continuity

- **API Security**
  - API key authentication via headers

---

## System Architecture
Client → FastAPI Endpoint → Scam Detector
→ Conversation Agent
→ Regex Intelligence Extractor
→ Session & Intelligence Store

---

## Tech Stack

- **Backend:** Python, FastAPI
- **Regex Engine:** Python `re`
- **API Server:** Uvicorn
- **Testing:** Swagger UI (`/docs`)
- **Version Control:** Git & GitHub

## 📡 API Endpoint

### POST `/api/message`

#### Headers

### Team Contributions
Member	Responsibility
Anitesh	API + Logic Integration
Ayush	Agent Reply Strategy
Anand	Regex Intelligence Extraction
Soumyadeep	Deployment & Testing

## Team Contributions
Member	Responsibility
Anitesh	API + Logic Integration
Ayush	Agent Reply Strategy
Anand	Regex Intelligence Extraction
Soumyadeep	Deployment & Testing


