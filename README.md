# 🥗 NutriScan Pro
**AI-Powered Nutrition Intelligence** — built with Streamlit + Gemini 1.5 Flash.

Live Demo: [nutriscanscanner.streamlit.app](https://nutriscanscanner.streamlit.app/)

NutriScan Pro is a full-stack AI application designed to simplify calorie tracking. Instead of manually searching for every ingredient, users simply snap a photo. The AI analyzes the image, estimates portions, and provides a macro-nutrient breakdown that logs directly into a personalized dashboard.

---

## ✨ Features

- **🎨 Glassmorphism UI**: A modern, dark-themed interface with neon accents and frosted-glass components.
- **🤖 AI Vision Scanning**: Powered by **Gemini 1.5 Flash** to identify food items and estimate calories, protein, carbs, and fats from a single image.
- **🔐 Secure Authentication**: Built-in Login/Signup system using SQLite and SHA-256 password hashing.
- **🧮 Personalized Goals**: Calculates daily targets using the **Mifflin-St Jeor Equation** based on age, weight, height, and activity level.
- **📊 Progress Analytics**: Visualizes daily calorie consumption vs. goals and displays a 7-day trend chart using Plotly.
- **📱 Mobile Ready**: Fully responsive design, ready to be "Added to Home Screen" on iOS and Android.

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) (Python-based web framework)
- **AI/ML**: [Google Gemini 1.5 Flash](https://aistudio.google.com/) (Vision-Language Model)
- **Database**: [SQLite](https://www.sqlite.org/index.html) (Local relational storage)
- **Visualization**: [Plotly](https://plotly.com/) & [Pandas](https://pandas.pydata.org/)
- **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)

---

## 📂 Project Structure

```text
Nutriscan/
├── .streamlit/
│   └── secrets.toml     # (Local only) API Keys & Secrets
├── .gitignore           # Prevents secrets and DB from being leaked
├── app.py               # Main application logic & UI
├── database.py          # SQLite schema and database functions
├── requirements.txt     # List of Python dependencies
└── README.md            # Project documentation