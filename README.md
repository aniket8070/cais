# 🧠 CAIS — Current Affairs Intelligence System

> **AI-Powered Daily News Analyzer for Competitive Exam Students**  
> Upload any newspaper PDF → OCR extraction → LLaMA 3.3 generates sector-wise study notes for UPSC, MPSC, SSC, Banking, Railway exams.

---

## 🚀 Live Demo

🔗 **Deployed on Railway:** [cais-production.up.railway.app](https://cais-production.up.railway.app)

---

## 📸 Features

| Feature | Description |
|---|---|
| 📄 **PDF Upload** | Upload daily newspaper PDF (Indian Express, Hindu, etc.) |
| 🔍 **OCR Engine** | Tesseract OCR extracts text from encrypted/scanned PDFs |
| 🤖 **AI Notes** | Groq LLaMA 3.3 generates structured sector-wise notes |
| 💬 **Chat Mode** | Ask any current affairs question directly |
| 📋 **Paste Text** | Paste news article text for instant notes |
| 📧 **Email Summary** | Daily summary PDF sent via Gmail SMTP |
| 🔐 **Auth System** | Login/Logout with Django authentication |

---

## 🗂️ Sector-Wise Notes Generated

| # | Sector |
|---|---|
| 1 | 🏛️ Polity & Governance |
| 2 | 💰 Economy & Finance |
| 3 | 🌍 International Relations |
| 4 | 🔬 Science & Technology |
| 5 | 🌿 Environment & Ecology |
| 6 | 🏥 Health & Medicine |
| 7 | 📚 Education & Society |
| 8 | 🛡️ Defence & Security |
| 9 | 🌏 Geography & Disaster Management |
| 10 | 🧩 Miscellaneous |

Each sector generates:
- 📰 Key News & Headlines
- 📊 Important Facts & Data
- 📖 Key Terms & Concepts
- 🏛️ Constitutional / Legal / Policy Angle
- 🎯 Exam Relevance (UPSC / MPSC / SSC / Banking / Railway / NDA)
- 🔗 Background & Context

---

## 🛠️ Tech Stack

```
Backend      → Django 5.0
AI Model     → Groq API (LLaMA 3.3 70B Versatile)
OCR          → Tesseract OCR + Poppler (pdf2image)
PDF Parse    → pdfminer.six, PyMuPDF, pypdf
Database     → PostgreSQL (Railway) / SQLite (local)
Deployment   → Railway.app + GitHub CI/CD
Email        → Gmail SMTP + ReportLab (PDF generation)
Frontend     → HTML / CSS / JavaScript (ChatGPT-style UI)
Auth         → Django built-in authentication
```

---

## ⚙️ Local Setup

### 1. Clone the repo
```bash
git clone https://github.com/aniket8070/cais.git
cd cais
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install Tesseract OCR
- **Windows:** Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- Install to: `C:\Program Files\Tesseract-OCR\`

### 5. Install Poppler
- **Windows:** Download from [oschwartz10612/poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases)
- Extract to: `C:\Release-25.12.0-0\poppler-25.12.0\Library\bin`

### 6. Create `.env` file
```env
SECRET_KEY=your-django-secret-key
DEBUG=False
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 7. Run migrations & create superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 8. Start the server
```bash
python manage.py runserver
```
Open: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📁 Project Structure

```
cais/
├── cais/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── chatbot/               # Main app
│   ├── ai_service.py      # Groq LLaMA integration
│   ├── pdf_reader.py      # OCR + PDF text extraction
│   ├── views.py           # Upload, Chat, Sector views
│   ├── models.py
│   └── templates/
│       └── chat.html      # ChatGPT-style UI
├── requirements.txt
├── manage.py
└── README.md
```

---

## 🔄 Daily Workflow

```
1. Download Indian Express / The Hindu epaper PDF
       ↓
2. Upload PDF on CAIS → OCR processes ~15 pages (~4 min)
       ↓
3. 10 sector buttons appear
       ↓
4. Click any sector → AI generates detailed exam-ready notes
       ↓
5. Use Chat tab to ask follow-up questions
```

---

## 💡 Use Cases

- 🎓 UPSC / MPSC / UPSC CSE aspirants
- 🏦 Banking exams — IBPS PO, SBI PO, RBI Grade B
- 🚂 Railway — RRB NTPC, Group D
- 📋 SSC — CGL, CHSL, MTS
- 🪖 Defence — NDA, CDS, AFCAT

---

## 🧑‍💻 Author

**Aniket Dhuke**  
🔗 [GitHub](https://github.com/aniket8070) | 💼 Data Science & AI/ML Projects

---

## 📄 License

This project is for educational and portfolio purposes.

---

⭐ **If this project helped you, please give it a star!**
