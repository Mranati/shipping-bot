import math
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from rapidfuzz import process

TOKEN = os.getenv("TOKEN")

# --- الأسعار حسب المنطقة ---
zone_prices = {
    "1": (12, 5),
    "2": (12, 5),
    "3": (18, 8),
    "4": (19, 8),
    "5": (20, 12),
    "A": (28, 16)
}

# --- الاستثناءات ---
special_cases = {
    "السعودية": lambda w: (15 if w <= 0.5 else 15 + math.ceil((w - 0.5) / 0.5) * 5),
    "سوريا": lambda w: 35 if w <= 2 else 35 + math.ceil((w - 2) / 0.5) * 12,
    "لبنان": lambda w: 35 if w <= 2 else 35 + math.ceil((w - 2) / 0.5) * 12,
    "العراق": lambda w: 30 if w <= 2 else 30 + math.ceil((w - 2) / 0.5) * 8,
    "تركيا": lambda w: 30 if w <= 2 else 30 + math.ceil((w - 2) / 0.5) * 8
}

# --- دول مناطق الحرب ---
war_zone_extra = ["العراق", "فلسطين", "ليبيا", "اليمن", "سوريا"]

from country_zone_map_full import country_zone_map

# --- دالة مطابقة تقريبية للاسم ---
def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة")  # تصحيح الهاء ↔ التاء المربوطة
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

# --- تعديل خاص لفلسطين ---
special_cases_palestine = {
    "الضفة": lambda w: (11 if w <= 2 else 11 + math.ceil((w - 2) / 0.5) * 5),
    "القدس": lambda w: (13 if w <= 2 else 13 + math.ceil((w - 2) / 0.5) * 5),
    "الداخل": lambda w: (20 if w <= 2 else 20 + math.ceil((w - 2) / 0.5) * 5)
}

# --- دالة الحساب ---
def calculate_shipping(country, qty_or_weight, season, area=None):
    if "كغ" in qty_or_weight or "kg" in qty_or_weight.lower():
        # إذا تم إدخال الوزن
        weight = float(qty_or_weight.replace("كغ", "").replace("kg", ""))
    else:
        # إذا كان يتم استخدام عدد القطع
        weight = int(qty_or_weight) * (0.5 if season in ["صيفي", "صيفية"] else 1)

    # تحقق من استثناءات فلسطين أولاً
    if country == "فلسطين":
        if area in special_cases_palestine:
            price = special_cases_palestine[area](weight)
            return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → {area}"

    # تحقق من استثناءات أولاً
    if country in special_cases:
        price = special_cases[country](weight)
        if isinstance(price, tuple):
            return f"السعر: {price[0]} / {price[1]} / {price[2]} دينار\nالتفاصيل: استثناء خاص ({country})"
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country})"

    # منطقة الدولة
    zone = country_zone_map.get(country)
    if not zone:
        return "❌ الدولة غير مدرجة في قائمة الشحن"

    base, extra = zone_prices[zone]
    if weight <= 0.5:
        total = base
    else:
        total = base + math.ceil((weight - 0.5) / 0.5) * extra

    if country in war_zone_extra and country not in ["فلسطين", "سوريا", "لبنان", "العراق", "تركيا"]:
        total += 15
        return f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {base} + إضافات حرب + وزن إضافي"

    return f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {base} + وزن إضافي"

# --- الرد على الرسائل ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) != 3 and len(parts) != 4:
            await update.message.reply_text("⚠️ يرجى إدخال: فلسطين [المنطقة] [عدد القطع أو الوزن] [الموسم (صيفية/شتوية)]")
            return

        raw_country, region, qty_or_weight, season = parts[:4]

        # ✅ التصحيح الإملائي للموسم
        if season in ["صيفي", "صيفية"]:
            season = "صيفية"
        elif season in ["شتوي", "شتوية"]:
            season = "شتوية"
        else:
            await update.message.reply_text("⚠️ نوع القطع يجب أن يكون صيفية أو شتوية فقط")
            return

        # ✅ المطابقة التقريبية لاسم الدولة
        country = match_country(raw_country, list(country_zone_map.keys()) + list(special_cases.keys()))
        if not country:
            await update.message.reply_text("❌ الدولة غير معروفة")
            return

        # ✅ إذا كانت فلسطين يجب أن يذكر المنطقة
        if country == "فلسطين" and region not in ["الضفة", "القدس", "الداخل"]:
            await update.message.reply_text("⚠️ يرجى تحديد المنطقة داخل فلسطين: الضفة، القدس أو الداخل")
            return

        # ✅ التحقق إذا القيمة وزن أو عدد قطع
        response = calculate_shipping(country, qty_or_weight, season, region)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# --- تشغيل البوت ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
