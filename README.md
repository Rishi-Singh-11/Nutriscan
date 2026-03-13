# 🥗 NutriScan Pro

**AI-Powered Nutrition Intelligence** — built with Streamlit + Gemini 1.5 Flash.

Upload a photo of any meal and get instant calorie & macro breakdowns, tracked against your personalized daily goal.

---

## Project Structure

```
nutriscan-pro/
├── app.py                  # Main Streamlit app — UI, routing, AI calls
├── database.py             # "The Accountant" — all SQLite logic
├── requirements.txt        # Python dependencies
├── .gitignore              # Keeps your secrets & DB local
└── .streamlit/
    └── secrets.toml        # 🔒 LOCAL ONLY — your API key vault
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/yourname/nutriscan-pro.git
cd nutriscan-pro
pip install -r requirements.txt
```

### 2. Add your Gemini API key

Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey), then:

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "your_key_here"
```

### 3. Run

```bash
streamlit run app.py
```

---

## Features

| Feature | Detail |
|---|---|
| 🔐 Auth | SQLite-backed login/signup with SHA-256 hashed passwords |
| 🧮 Calorie Goal | Mifflin-St Jeor equation + activity multiplier + goal adjustment |
| 🤖 AI Scan | Gemini 1.5 Flash analyzes food photos → JSON macros |
| 📊 Dashboard | Metric cards, progress bar, weekly Plotly trend chart |
| 🍽️ Meal Log | Per-user daily meal history with macro breakdowns |
| 🎨 UI | Glassmorphism dark theme with neon cyan accents |

---

## Tech Stack

- **Frontend**: Streamlit + custom CSS Glassmorphism
- **AI**: Google Gemini 1.5 Flash (`google-generativeai`)
- **Database**: SQLite via Python `sqlite3` (zero config)
- **Charts**: Plotly
- **Nutrition math**: Mifflin-St Jeor BMR equation

---

## Security Notes

- `GEMINI_API_KEY` lives only in `.streamlit/secrets.toml` — never committed
- `nutriscan.db` is gitignored — user data stays local
- Passwords are SHA-256 hashed before storage
