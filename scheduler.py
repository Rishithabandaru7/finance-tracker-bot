import os
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from database import get_weekly_summary, get_all_users
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

def build_summary_message(rows, title):
    if not rows:
        return f"📊 *{title}*\n\nNo transactions this week!"

    income_lines = []
    expense_lines = []
    total_income = 0
    total_expense = 0

    for type_, category, amount in rows:
        if type_ == "income":
            income_lines.append(f"  • {category.title()}: ₹{amount:,.0f}")
            total_income += amount
        else:
            expense_lines.append(f"  • {category.title()}: ₹{amount:,.0f}")
            total_expense += amount

    msg = f"📊 *{title}*\n\n"

    if income_lines:
        msg += "💰 *Income*\n" + "\n".join(income_lines)
        msg += f"\n  Total: ₹{total_income:,.0f}\n\n"

    if expense_lines:
        msg += "💸 *Expenses*\n" + "\n".join(expense_lines)
        msg += f"\n  Total: ₹{total_expense:,.0f}\n\n"

    savings = total_income - total_expense
    emoji = "✅" if savings >= 0 else "⚠️"
    msg += f"{emoji} *Net: ₹{savings:,.0f}*"
    return msg

async def send_all_summaries():
    users = get_all_users()
    for user_id, first_name in users:
        rows = get_weekly_summary(user_id)
        msg = build_summary_message(rows, f"Weekly Summary — {first_name}")
        try:
            await bot.send_message(
                chat_id=user_id,
                text=msg,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Could not send to {first_name}: {e}")

def send_weekly_to_all():
    asyncio.run(send_all_summaries())

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_weekly_to_all,
        trigger="cron",
        day_of_week="sun",
        hour=20,
        minute=0
    )
    scheduler.start()
    return scheduler