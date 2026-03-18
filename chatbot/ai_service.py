import json
import os
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
client = Groq(api_key=GROQ_API_KEY)
MODEL = "llama-3.3-70b-versatile"

SECTORS = [
    "Polity & Governance",
    "Economy & Finance",
    "Environment & Ecology",
    "Science & Technology",
    "International Relations",
    "Social Issues & Welfare",
    "Defence & Security",
    "Health",
    "Education",
    "Geography & Disaster Management",
]

SYSTEM_PROMPT = """You are CAIS — Current Affairs Intelligence System.
You prepare students for ALL Indian competitive exams: UPSC, MPSC, SSC CGL, IBPS/SBI Banking, RBI Grade B, Railway RRB, NDA, CDS, State PSCs.
Your notes are detailed, analytical, factual, and exam-focused at UPSC depth level.
IMPORTANT: Extract ONLY information present in the given newspaper text. Do NOT hallucinate or add general knowledge not in the text."""


def _ask_groq(prompt, max_tokens=2048):
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            model=MODEL,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq Error: {e}")
        return None


def generate_sector_notes(text):
    """Sector-wise 1-line summary dict"""
    # Use first 4000 chars for sector detection
    chunk = text[:4000] if len(text) > 4000 else text

    if len(chunk.strip()) < 100:
        return {sector: "PDF text could not be extracted." for sector in SECTORS}

    prompt = f"""Read this Indian newspaper text carefully and classify news into sectors.

For each sector, write a 1-2 sentence summary of relevant news found in the text. If no relevant news found for a sector, write "No major news".

Return ONLY valid JSON — no markdown, no extra text:
{{
  "Polity & Governance": "...",
  "Economy & Finance": "...",
  "Environment & Ecology": "...",
  "Science & Technology": "...",
  "International Relations": "...",
  "Social Issues & Welfare": "...",
  "Defence & Security": "...",
  "Health": "...",
  "Education": "...",
  "Geography & Disaster Management": "..."
}}

NEWSPAPER TEXT:
{chunk}

JSON:"""

    result = _ask_groq(prompt, max_tokens=1200)
    if result:
        try:
            start = result.find('{')
            end = result.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(result[start:end])
        except json.JSONDecodeError:
            pass
        return {"_raw": result}

    return {sector: "Could not load — try again" for sector in SECTORS}


def get_sector_detail(text, sector):
    """Detailed notes for one sector from the newspaper"""
    # Use more text for detailed analysis
    chunk = text[:6000] if len(text) > 6000 else text

    prompt = f"""You are a UPSC Current Affairs expert. Extract ALL news about "{sector}" from this newspaper text and write comprehensive exam-ready notes.

STRICT RULE: Only use information present in the newspaper text below. Do NOT add outside knowledge.

Write notes in this format:

## {sector}

### 📰 Key News & Headlines
- **[Headline/Topic]**: Detailed explanation with context (2-3 lines each)
(List ALL relevant news items found)

### 📊 Important Facts & Data
- Key numbers, statistics, names, dates, places from the article
- Policy names, scheme names, organizations mentioned

### 📖 Key Terms & Concepts
- **Term**: Simple definition relevant to the news

### 🏛️ Constitutional / Legal / Policy Angle
- Relevant Articles, Acts, Schemes connected to this news

### 🎯 Exam Relevance
- **UPSC/MPSC Prelims**: Key facts to memorize
- **UPSC/MPSC Mains**: Analysis points
- **SSC/Railway**: Quick recall points
- **Banking (IBPS/SBI/RBI)**: Finance/economy angle if applicable

### 🔗 Background Context
- Why this news matters, historical background

Write minimum 400 words. Be thorough.

NEWSPAPER TEXT:
{chunk}

Detailed notes for {sector}:"""

    result = _ask_groq(prompt, max_tokens=2500)
    return result if result else f"❌ Could not generate {sector} notes. Please try again."


def answer_question(question):
    """Chat question answer"""
    prompt = f"""Answer this current affairs question for Indian competitive exam students.

### {question}

**📌 Key Facts:**
- Important points in bullets

**📖 Key Terms:**
- **Term**: Definition

**🏛️ Constitutional / Legal Angle:**
- Articles, Acts, Committees (if applicable)

**📊 Important Data / Statistics:**
- Numbers, dates, rankings

**🎯 Exam Relevance:**
- UPSC/MPSC: What to focus on
- SSC/Railway: Quick points
- Banking: Finance angle if applicable

**🔗 Recent Developments:**
- Latest news on this topic

Question: {question}"""

    result = _ask_groq(prompt, max_tokens=1800)
    return result if result else "❌ Could not get answer. Please try again."