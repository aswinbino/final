# ClauseGuard AI 🛡️
> **Explainable, Personalized NLP Framework for Contract Risk Assessment & Evidence-Grounded Decision Support**

ClauseGuard AI is a full-stack, enterprise-grade legal technology platform that analyzes legal agreements, classifies clauses, identifies risky and unfavorable conditions, computes personalized risk scores based on user roles, traces interconnected risk chains, simulates what-if dispute scenarios, and generates evidence-grounded reports.

---

## 🏗️ 1. Architecture & Tech Stack

```
                             ClauseGuard AI
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
   React 18 Frontend                               FastAPI Python Backend
  (Tailwind/Vanilla CSS                              (REST API Service)
   Recharts / Lucide / Dropzone)                             │
                                        ┌────────────────────┼────────────────────┐
                                        ▼                    ▼                    ▼
                                 Document Parsers        NLP Engine         Database Layer
                                 • PyMuPDF (.pdf)        • Sentence-Trans    • SQLite / Postgres
                                 • python-docx (.docx)   • FAISS Vectors     • SQLAlchemy Async
                                                         • Risk Lexicon      • ReportLab (PDF)
```

- **Frontend:** React 18, Vite, Lucide Icons, Recharts, Custom Glassmorphic Dark Design System.
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), Uvicorn.
- **NLP & Vectors:** Hugging Face `transformers`, `sentence-transformers` (`all-MiniLM-L6-v2`), `faiss-cpu`, Scikit-learn.
- **Document Parsers:** `PyMuPDF` (for high-fidelity PDF extraction) and `python-docx` (for DOCX files).
- **Report Generation:** `ReportLab` for automated PDF export.

---

## 🧩 2. Core System Modules Implemented

| Module | Name | Endpoint | Description |
|---|---|---|---|
| **Module 1** | Contract Upload & Parsing | `POST /api/v1/upload` | Parses `.pdf` and `.docx` contracts, cleans text, segments clauses |
| **Module 2** | Clause Extraction & Classification | `POST /api/v1/extract-clauses/{id}` | Identifies and categorizes clauses into 10 legal types (Payment, Liability, etc.) |
| **Module 3** | Risk Assessment & Severity | `POST /api/v1/risk-analysis` | Flags risky terms and calculates severity scores (`Low`, `Medium`, `High`) |
| **Module 4** | Personalized User Context Engine | `POST /api/v1/risk-analysis` (role) | Re-weights risks for Freelancers, Tenants, Employees, Business Owners, Vendors |
| **Module 5** | Clause Relationship & Risk Chains | `POST /api/v1/risk-analysis` | Traces multi-clause cascading dependencies (e.g. Payment -> Penalty -> Termination) |
| **Module 6** | What-If Impact Analysis | `POST /api/v1/what-if` | Interactive query terminal answering scenario questions with consequence tracing |
| **Module 7** | Evidence-Grounded Explanation (XAI) | Built into Modules 2, 3, 6, 10 | Verbatim quotes mapped directly to page number and source clause |
| **Module 8** | Obligation & Deadline Extraction | `POST /api/v1/obligations/{id}` | Extracts payment timelines, notice periods, and renewal deadlines |
| **Module 9** | Contract Comparison & Revisions | `POST /api/v1/compare` | Side-by-side diff comparing two versions with risk escalation tags |
| **Module 10** | Decision Support & Reports | `POST /api/v1/report` | Generates comprehensive JSON reports and downloadable PDF summaries |

---

## 🚀 3. Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/api/docs`
- Health Check: `http://localhost:8000/health`

### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
- App UI: `http://localhost:5173`

---

## ⚡ 4. Instant 1-Click Demo Contracts

ClauseGuard AI includes pre-loaded sample agreements with real-world legal traps:
1. **Freelance Software Development Agreement (High Risk):** Contains Net 90 payment terms, perpetual moral rights waivers, unlimited liability, 3-year global non-compete, $500/day penalties, and Cayman Islands / Swiss arbitration.
2. **Commercial Property Lease (Landlord-Biased):** Contains 180-day renewal notice periods, 15% weekly compounded late fees, deposit forfeiture, tenant-assumed HVAC structural repairs, and unilateral rule modifications.
