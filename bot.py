import math
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

TOKEN = os.environ.get("TOKEN")

zone_prices = {
    "1": (12, 5),
    "2": (12, 5),
    "3": (18, 8),
    "4": (19, 8),
    "5": (20, 12),
    "A": (28, 16)
}

special_cases = {
    "السعودية": lambda w: (15 if w <= 0.5 else 15 + math.ceil((w - 0.5) / 0.5) * 5),
    "فلسطين": lambda w: (
        11 if w <= 2 else 11 + math.ceil((w - 2) / 0.5) * 5,
        13 if w <= 2 else 13 + math.ceil((w - 2) / 0.5) * 5,
        20 if w <= 2 else 20 + math.ceil((w - 2) / 0.5) * 5
    ),
    "سوريا": lambda w: 35 if w <= 2 else 35 + math.ceil((w - 2) / 0.5) * 12,
    "لبنان": lambda w: 35 if w <= 2 else 35 + math.ceil((w - 2) / 0.5) * 12,
    "العراق": lambda w: 30 if w <= 2 else 30 + math.ceil((w - 2) / 0.5) * 8,
    "تركيا": lambda w: 30 if w <= 2 else 30 + math.ceil((w - 2) / 0.5) * 8
}

war_zone_extra = ["Iraq", "Palestine", "Libya", "Yemen", "Syria"]

# اختصار: هذا مثال مصغّر من قائمة الدول
country_zone_map = {
    "India": "2",
    "Lebanon": "1",
    "Syria": "1",
    "Iraq": "3",
    "Turkey": "3",
    "Saudi Arabia": "2",
    "USA": "4",
    "Germany": "3",
    "Jordan": "2",
    "Morocco": "3"
}

def calculate_shipping(country: str, quantity: int, season: str) -> str:
    weight_per_piece = 0.5 if season == "صيفية" else 1
    total_weight = quantity * weight_per_piece
    total_weight = math.ceil(total_weight * 2) / 2

    if country in special_cases:
        if country == "فلسطين":
            prices = special_cases[country](total_weight)
            return f"السعر: {prices[0]} دينار / التفاصيل: {total_weight} كغ → فلسطين - الضفة → {prices[0]}"
        price = special_cases[country](total_weight)
        return f"السعر: {price} دينار / التفاصيل: {total_weight} كغ → {country} (استثناء)"

    zone = country_zone_map.get(country)
    if not zone:
        return "❌ الدولة غير مدرجة. تأكد من الإملاء أو التواصل مع الدعم."

    base, extra = zone_prices[zone]
    if total_weight <= 0.5:
        price = base
        additions = 0
    else:
        additional = math.ceil((total_weight - 0.5) / 0.5)
        additions = additional * extra
        price = base + additions

    if "(W)" in country or country in war_zone_extra:
        if country not in ["سوريا", "لبنان", "العراق", "تركيا"]:
            price += 15
            return f"السعر: {price} دينار / التفاصيل: {total_weight} كغ → المنطقة {zone} → {base} + {additions} + 15 (رسوم حرب)"

    return f"السعر: {price} دينار / التفاصيل: {total_weight} كغ → المنطقة {zone} → {base} + {additions}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        parts = text.split()
        if len(parts) != 3:
            await update.message.reply_text("⚠️ الرجاء إرسال الرسالة بالشكل التالي: اسم الدولة عدد_القطع نوعها (صيفية/شتوية)")
            return
        country, qty, season = parts
        quantity = int(qty)
        if season not in ["صيفية", "شتوية"]:
            await update.message.reply_text("⚠️ نوع القطع يجب أن يكون صيفية أو شتوية فقط")
            return
        response = calculate_shipping(country, quantity, season)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()