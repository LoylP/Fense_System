# 🛡️ FRAUDINTEL: An Automated System for Detecting and Verifying Fake News in Online Fraud Campaigns Using LLMs

FRAUDINTEL is a multi-agent AI system designed to automatically verify information and detect fake news across various online fraud campaigns. It integrates **Large Language Models (LLMs)**, **Retrieval-Augmented Generation (RAG)**, and domain-specific tools to verify URLs, emails, and social media content.  
Built with **FastAPI**, **Next.js**, and **Docker**, the system ensures modularity, performance, and real-time interaction.

---

## 🚀 Features

- ✅ Multi-Agent Architecture for modular information verification
- 🔍 Fact-checking via API, Google search, domain/IP analysis, and internal DB
- 🧠 LLM-powered reasoning and final judgment
- 📌 Mapping to known TTP (Tactics, Techniques, Procedures) patterns
- 🌐 Built-in news crawler and Vietnamese fake news dataset
- 📊 End-to-end processing from user input to verified output

---

## 🧠 System Architecture

![Multi-Agent Architecture](/public/Workflow_MultiAgent.png)

### Agents & Responsibilities:

- **Agent 1 – Input Analyzer**: Extracts key entities and input types
- **Agent 2 – Entity Checker**: Verifies reliability of emails, phones, URLs using APIs
- **Agent 3 – Domain Analyst**: Analyzes domain/IP via Whois
- **Agent 4 – Web Researcher**: Performs Google search to find supportive info
- **Agent 5 – DB Researcher**: Retrieves evidence from internal knowledge base
- **Agent 6 – Final Verifier**: Synthesizes evidence and makes verdict
- ✅ If input is fake → maps to **TTP patterns**

---

## 📊 Dataset & Preprocessing

### 📁 Base Datasets

- **Utilizing Transformer Models to Detect Vietnamese Fake News on Social Media Platforms**
- **Detecting Vietnamese Fake News**  
  → Both datasets provide Vietnamese text labeled as `real` or `fake`.

### 🌐 Augmented Data

Collected automatically from trusted news sites in Vietnam (e.g., **VnExpress**, **Dân Trí**, **VTV**, etc.) using a custom `BeautifulSoup` web crawler and stored via API in the database.

Each article includes:

- Title
- Content
- Date Published
- Article Link

### 📊 Data Distribution

| Label     | Total     | Train     | Val     | Test    |
| --------- | --------- | --------- | ------- | ------- |
| Fake      | 2,299     | 1,391     | 454     | 454     |
| Real      | 1,922     | 1,143     | 389     | 390     |
| **Total** | **4,221** | **2,534** | **843** | **844** |

---

## ⚙️ Technology Stack

| Component      | Stack                               |
| -------------- | ----------------------------------- |
| Backend API    | FastAPI                             |
| Frontend UI    | Next.js                             |
| AI Models      | LLMs (Mistral, LLaMA3, Qwen, Gemma) |
| Data Retrieval | BM25 + Embedding + Rerank           |
| Crawler        | BeautifulSoup + REST API            |
| Deployment     | Docker + Docker Compose             |
| Database       | SQLite + FAISS (VectorDB)           |

---

## 🧪 Model Evaluation

We evaluated both **zero-shot** and **fine-tuned** variants of popular open LLMs:

| Model            | Accuracy   | F1-Score   | Precision  | Recall     | URC   |
| ---------------- | ---------- | ---------- | ---------- | ---------- | ----- |
| **Zero-shot**    |            |            |            |            |       |
| Mistral-7B       | 0.455      | 0.4684     | 0.7081     | 0.455      | 194   |
| LLaMA3.2-3B      | 0.6315     | 0.6718     | 0.7275     | 0.6315     | 114   |
| Qwen2.5-3B       | 0.6647     | 0.6371     | 0.7623     | 0.6647     | 33    |
| Meta-LLaMA3.1-8B | 0.609      | 0.5678     | 0.7099     | 0.609      | 44    |
| Gemma2-9B        | 0.7737     | 0.7809     | 0.7929     | 0.7737     | 20    |
| **Fine-Tuned**   |            |            |            |            |       |
| LLaMA3.2-3B      | 0.8021     | 0.8155     | 0.8335     | 0.8021     | 26    |
| Qwen2.5-3B       | 0.8199     | 0.8229     | 0.8448     | 0.8199     | 14    |
| Meta-LLaMA3.1-8B | 0.7654     | 0.7733     | 0.8394     | 0.7654     | 30    |
| Gemma2-9B        | **0.9159** | **0.9160** | **0.9193** | **0.9159** | **0** |

---

## 📦 Installation Guide

### 1. Clone the repository

```bash
git clone https://github.com/LoylP/Fraudintel.git
cd Fraudintel
```

### 2. Setup .env file

Create a .env file at project root:

```bash
OPENAI_API_KEY=
VT_API_KEY=
ABSTRACT_EMAIL_API=
ABSTRACT_PHONE_API=
API_GOOGLE_CREDENTIAL=
SEARCH_ENGINE_CSE_ID=
NEXT_PUBLIC_API_URL= ##Port FastAPI 8000
DB_PATH=data/news.db
VECTORDB_PATH=data/vector.index
```

You can get VT_API_KEY at: https://www.virustotal.com and ABSTRACT_API at: https://www.abstractapi.com

### 3. Run Backend (FastAPI)

```bash
python -m venv env
source env/bin/activate # On Windows: env\Scripts\activate
pip install -r requirements.txt
python app.py
```

### 4. Run Frontend (Next.js)

```bash
cd my-app
npm install
npm run dev
```

## 🐳 Docker Deployment

If you prefer Docker, run:

```bash
docker compose up --build -d
```

This will launch FastAPI and Next.js services with .env integrated.

## 🔁 Usage Flow

### 1. User submits a query (text, screenshot, or URL)

### 2. Input Analyzer extracts core information

### 3. Agents check:

- API data (email, phone, link)
- Domain/IP metadata
- Google Search for supporting facts
- Internal DB using hybrid search

### 4. Final Verifier aggregates evidence and gives verdict

### 5. If fake → matched against known TTP patterns

## 📄 Publication

This project has been submitted to NSS 2025 under the title:

**FraudTrace: Verifying Fraudulent News to Prevent Online Scam Campaigns via a Multi-Agent LLM-Based System**

You can view the sample paper here:

```bash
/public/NSS2025_Phishing_Campaign.pdf
```
