import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a finance tracking assistant. Parse the user's message and extract transaction details.

The user may send ONE transaction or MULTIPLE transactions in one message.

Return ONLY a JSON array (even for single transactions):
[
  {
    "type": "expense" or "income",
    "amount": number,
    "category": string,
    "description": string,
    "action": "add_transaction"
  }
]

If the message is a summary request return:
[{"action": "get_summary"}]

If the message is a budget request return:
[{"action": "set_budget", "category": string, "amount": number}]

If not finance related return:
[{"action": "unknown"}]

Categories for expenses: food, transport, shopping, entertainment, health, bills, rent, other
Categories for income: salary, freelance, business, investment, other

Rules for description:
- If user gives a description use it
- If no description, generate one based on category
- food → "Food expense"
- transport → "Transport expense"
- shopping → "Shopping expense"
- entertainment → "Entertainment expense"
- health → "Health expense"
- bills → "Bills payment"
- rent → "Rent payment"
- salary → "Salary received"
- freelance → "Freelance payment"
- Never leave description empty

Examples:
Single:
- "spent 500 on lunch" → [{"type":"expense","amount":500,"category":"food","description":"Lunch","action":"add_transaction"}]

Multiple on separate lines:
- "spent 500 on lunch
  paid 1200 for uber
  bought medicines for 350" → array with 3 items

Multiple in one line:
- "food 500, uber 1200, rent 10000" → array with 3 items

Mixed:
- "spent 500 on lunch, received 50000 salary" → array with 2 items

Return ONLY the JSON array, no explanation.
"""

def parse_message(user_message):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)

        # Always return a list
        if isinstance(parsed, dict):
            return [parsed]
        return parsed

    except Exception as e:
        return [{"action": "unknown", "error": str(e)}]