<h1 align="center">💰 AI-Powered Personal Finance Tracker Bot</h1>

<p align="center">
  A <b>Telegram bot</b> that tracks your expenses using <b>natural language</b> — just type what you spent and the AI handles the rest.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white"/>
  <img src="https://img.shields.io/badge/Groq-FF6B35?style=for-the-badge&logo=data:image/svg+xml;base64,&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white"/>
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white"/>
</p>

---

## ✨ Features

- 💬 **Natural Language Expense Logging** — Type *"spent 150 on lunch"* and the bot categorizes and saves it automatically
- 🗂️ **10+ Auto-Categories** — Food, Transport, Shopping, Entertainment, Health, Bills, and more
- 📊 **Monthly Summaries** — View spending breakdowns by category on demand
- 🚨 **Budget Alerts** — Get notified at 80% and 100% of your monthly budget
- 👥 **Multi-User Support** — Each user has fully isolated data via Supabase PostgreSQL
- ⏰ **Scheduled Reports** — Automated monthly summaries via APScheduler
- ☁️ **24/7 Deployment** — Hosted on Render with persistent uptime

---

## 🏗️ Architecture

```
User (Telegram)
      │
      ▼
  bot.py  ──── Groq API (LLaMA 3.3 70B)
      │              │
      │         groq_parser.py
      │         (NLP: extract amount, category, description)
      │
      ▼
  database.py
      │
      ▼
Supabase PostgreSQL  (per-user data isolation)
      │
      ▼
  scheduler.py  (APScheduler — monthly reports)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| Bot Framework | python-telegram-bot |
| AI / NLP | Groq API — LLaMA 3.3 70B |
| Database | Supabase (PostgreSQL) |
| Scheduler | APScheduler |
| Deployment | Render (free tier, 24/7) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Groq API Key ([console.groq.com](https://console.groq.com))
- Supabase project with PostgreSQL

### Installation

```bash
# Clone the repo
git clone https://github.com/Rishithabandaru7/finance-tracker-bot.git
cd finance-tracker-bot

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
```

### Run Locally

```bash
python bot.py
```

---

## 💬 Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message and setup |
| `/help` | List all available commands |
| `/summary` | View this month's spending by category |
| `/setbudget <amount>` | Set your monthly budget limit |
| `/history` | View recent transactions |
| `/clear` | Clear all your expense data |

**Or just type naturally:**
- *"spent 200 on groceries"*
- *"paid 500 for electricity bill"*
- *"coffee 80 rupees"*

---

## 📁 Project Structure

```
finance-tracker-bot/
├── bot.py            # Main bot logic and command handlers
├── groq_parser.py    # AI-powered NLP expense parsing
├── database.py       # Supabase PostgreSQL operations
├── scheduler.py      # Automated monthly report scheduler
├── requirements.txt  # Python dependencies
└── .gitignore
```

---

## ☁️ Deployment on Render

This bot is deployed on [Render](https://render.com) as a background worker service.

1. Push code to GitHub
2. Create a new **Background Worker** on Render
3. Set environment variables in Render dashboard
4. Deploy — Render keeps the bot running 24/7

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ by <a href="https://github.com/Rishithabandaru7">Rishitha Bandaru</a></p>
