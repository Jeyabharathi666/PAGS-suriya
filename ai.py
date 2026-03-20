import os
import json
from collections import Counter
import gspread
from groq import Groq
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from zoneinfo import ZoneInfo

# =========================
# CONFIG
# =========================
SHEET_ID = "1YkTXNX5LAhANICxzu4Tj4Hr6aFMoXdufH_ev1gmRx7c"
INPUT_WS = "vivek"
OUTPUT_WS = "result"

# =========================
# GOOGLE AUTH (FROM SECRET)
# =========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SHEET_ID)

# input sheet
input_ws = spreadsheet.worksheet(INPUT_WS)

# create output if not exists
try:
    output_ws = spreadsheet.worksheet(OUTPUT_WS)
except:
    output_ws = spreadsheet.add_worksheet(title=OUTPUT_WS, rows="1000", cols="20")

# =========================
# GROQ
# =========================
groq = Groq(api_key=os.environ["GROQ_API_KEY"])

# =========================
# READ DATA
# =========================
up_data = input_ws.get("A4:Z11")
down_data = input_ws.get("AJ4:BI11")

# =========================
# EXTRACT STRENGTH
# =========================
def extract_strength(data):
    flat = []
    for row in data:
        for cell in row:
            if cell and cell.lower() != "symbol":
                flat.append(cell.strip())
    return Counter(flat)

up_counts = extract_strength(up_data)
down_counts = extract_strength(down_data)

# =========================
# BUILD DATA
# =========================
combined = []

all_stocks = set(list(up_counts.keys()) + list(down_counts.keys()))

for stock in all_stocks:
    combined.append({
        "stock": stock,
        "up": up_counts.get(stock, 0),
        "down": down_counts.get(stock, 0)
    })

# =========================
# AI
# =========================
def analyze(data):

    text = "\n".join([
        f"{d['stock']} | UP:{d['up']} | DOWN:{d['down']}"
        for d in data
    ])

    prompt = f"""
You are a professional short-term trader.

Data:
{text}

Predict next 1-2 day movement.

Return ONLY JSON:

[
  {{
    "stock": "name",
    "direction": "UP or DOWN",
    "probability": number (0-100),
    "strength": "weak/medium/strong"
  }}
]

Rules:
- High UP → UP
- High DOWN → DOWN
- Mixed → ignore
- Be selective
"""

    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

# =========================
# PROCESS
# =========================
results = []

try:
    output = analyze(combined)

    output = output.replace("```json", "").replace("```", "").strip()

    start = output.find("[")
    end = output.rfind("]") + 1

    data = json.loads(output[start:end])

    for row in data:
        if row["probability"] >= 65:
            results.append([
                row["stock"],
                row["direction"],
                row["probability"],
                row["strength"]
            ])

except Exception as e:
    print("AI ERROR:", e)

# =========================
# SORT
# =========================
results.sort(key=lambda x: x[2], reverse=True)

# =========================
# APPEND
# =========================
existing = output_ws.get_all_values()

if not existing:
    output_ws.append_row(["Stock", "Direction", "Probability", "Strength"])

for row in results:
    output_ws.append_row(row)

# =========================
# IST TIME
# =========================
ist = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")

output_ws.append_row(["Updated (IST)", ist])

last_row = len(output_ws.get_all_values())

output_ws.format(
    f"A{last_row}:B{last_row}",
    {
        "backgroundColor": {"red": 1, "green": 0.9, "blue": 1},
        "textFormat": {"bold": True}
    }
)

print("SUCCESS")
