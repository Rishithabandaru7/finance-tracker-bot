import os
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters, ContextTypes
)
from dotenv import load_dotenv
from database import (
    init_db, register_user, add_transaction,
    get_monthly_summary, set_budget, check_budget,
    get_recent_transactions, delete_transaction,
    delete_all_transactions
)
from groq_parser import parse_message
from scheduler import start_scheduler, build_summary_message

load_dotenv()

def get_user(update: Update):
    user = update.effective_user
    register_user(user.id, user.username, user.first_name)
    return user.id, user.first_name

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, first_name = get_user(update)
    msg = f"""👋 *Welcome {first_name}!*

I'm your personal Finance Tracker Bot.

💸 *Track Expenses:*
- "spent 500 on lunch"
- "paid 1200 for uber"
- "bought medicines for 350"

💰 *Track Income:*
- "received 50000 salary"
- "got 5000 freelance payment"

📊 *View Summary:*
- "show summary" or /summary

🎯 *Set Budgets:*
- "set food budget to 5000"
- /budget food 5000

Your data is *private* — nobody else can see it! 🔒"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, first_name = get_user(update)
    rows = get_monthly_summary(user_id)
    month = datetime.now().strftime("%B %Y")
    msg = build_summary_message(rows, f"{first_name}'s Summary — {month}")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, first_name = get_user(update)
    args = context.args
    if len(args) != 2:
        await update.message.reply_text(
            "Usage: /budget <category> <amount>\nExample: /budget food 5000"
        )
        return
    category = args[0].lower()
    try:
        limit = float(args[1])
        set_budget(user_id, category, limit)
        await update.message.reply_text(
            f"✅ Budget set!\n🏷️ Category: {category.title()}\n💰 Limit: ₹{limit:,.0f}/month"
        )
    except ValueError:
        await update.message.reply_text("❌ Amount must be a number.")
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, first_name = get_user(update)
    user_text = update.message.text
    await update.message.reply_text("⏳ Processing...")

    parsed_list = parse_message(user_text)

    # Handle summary and budget actions
    for parsed in parsed_list:
        action = parsed.get("action", "unknown")

        if action == "get_summary":
            await summary_command(update, context)
            return

        if action == "set_budget":
            amount   = parsed.get("amount")
            category = parsed.get("category", "other")
            if amount and category:
                set_budget(user_id, category, amount)
                await update.message.reply_text(
                    f"✅ Budget set!\n🏷️ {category.title()}: ₹{amount:,.0f}/month",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text("❌ Try: 'set food budget to 5000'")
            return

    # Filter only add_transaction actions
    transactions = [p for p in parsed_list if p.get("action") == "add_transaction"]

    if not transactions:
        await update.message.reply_text(
            "🤔 Didn't catch that.\n\nTry:\n"
            "• 'spent 200 on coffee'\n"
            "• 'received 30000 salary'\n"
            "• 'food 500, uber 1200, rent 10000'\n"
            "• 'show summary'"
        )
        return

    # Save all transactions
    reply = f"✅ *Recorded {len(transactions)} transaction(s)!*\n\n"

    for t in transactions:
        type_    = t.get("type")
        amount   = t.get("amount")
        category = t.get("category", "other")
        desc     = t.get("description", user_text)

        add_transaction(user_id, type_, amount, category, desc)

        emoji = "💸" if type_ == "expense" else "💰"
        reply += f"{emoji} ₹{amount:,.0f} | {category.title()} | {desc}\n"

        # Budget alert for expenses
        if type_ == "expense":
            spent, limit = check_budget(user_id, category)
            if limit:
                percent = (spent / limit) * 100
                if percent >= 100:
                    reply += f"   🚨 *Budget exceeded! {percent:.0f}% used*\n"
                elif percent >= 80:
                    reply += f"   ⚠️ *Budget warning! {percent:.0f}% used*\n"

    await update.message.reply_text(reply, parse_mode="Markdown")
async def recent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, first_name = get_user(update)
    rows = get_recent_transactions(user_id)

    if not rows:
        await update.message.reply_text("No transactions found!")
        return

    msg = "🧾 *Your Last 5 Transactions:*\n\n"
    for row in rows:
        id_, type_, amount, category, desc, date = row
        emoji = "💸" if type_ == "expense" else "💰"
        msg += f"{emoji} *#{id_}* — ₹{amount:,.0f} | {category.title()}\n"
        msg += f"   📝 {desc}\n"
        msg += f"   📅 {date}\n"
        msg += f"   To delete: `/delete {id_}`\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown")
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id, first_name = get_user(update)
    args = context.args

    # No argument given
    if len(args) == 0:
        await update.message.reply_text(
            "Usage:\n"
            "• `/delete <id>` — delete one transaction\n"
            "• `/delete all` — delete ALL transactions\n\n"
            "Use /recent to see transaction IDs",
            parse_mode="Markdown"
        )
        return

    # Delete ALL
    if args[0].lower() == "all":
        count = delete_all_transactions(user_id)
        if count > 0:
            await update.message.reply_text(
                f"✅ All {count} transactions deleted!\n\nFresh start! 🧹"
            )
        else:
            await update.message.reply_text(
                "❌ No transactions found to delete!"
            )
        return

    # Delete by ID
    try:
        transaction_id = int(args[0])
        success = delete_transaction(user_id, transaction_id)

        if success:
            await update.message.reply_text(
                f"✅ Transaction #{transaction_id} deleted!"
            )
        else:
            await update.message.reply_text(
                f"❌ Transaction #{transaction_id} not found!\n\nUse /recent to see your transactions."
            )
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid input.\n\n"
            "• `/delete 5` — delete transaction #5\n"
            "• `/delete all` — delete everything",
            parse_mode="Markdown"
        )
def main():
    init_db()
    scheduler = start_scheduler()
    print("✅ Database initialized")
    print("✅ Scheduler started")
    print("🤖 Multi-user bot is running...")

    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("summary", summary_command))
    app.add_handler(CommandHandler("budget", budget_command))
    app.add_handler(CommandHandler("recent", recent_command))
    app.add_handler(CommandHandler("delete", delete_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()