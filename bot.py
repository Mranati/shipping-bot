import math
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from rapidfuzz import process
import time

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

# --- استثناءات ---
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

# --- دول مناطق الحرب ---
war_zone_extra = ["العراق", "فلسطين", "ليبيا", "اليمن", "سوريا"]

from country_zone_map_full import country_zone_map

# --- دالة مطابقة تقريبية للاسم ---
def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة")  # تصحيح الهاء ↔ التاء المربوطة
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

# --- دالة الحساب ---
def calculate_shipping(country, quantity, season):
    weight = quantity * (0.5 if season == "صيفية" else 1)

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

        if len(parts) != 3:
            await update.message.reply_text("⚠️ يرجى إدخال: الدولة عدد القطع أو الوزن الموسم (صيفية/شتوية)")
            return

        raw_country, qty_or_weight, season = parts

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

        # ✅ التحقق إذا القيمة وزن أو عدد قطع
        if "كغ" in qty_or_weight or "kg" in qty_or_weight.lower():
            # إذا تم إدخال الوزن
            weight = float(qty_or_weight.replace("كغ", "").replace("kg", ""))
            if country in special_cases:
                price = special_cases[country](weight)
                if isinstance(price, tuple):
                    return await update.message.reply_text(f"السعر: {price[0]} / {price[1]} / {price[2]} دينار\nالتفاصيل: استثناء خاص ({country})")
                return await update.message.reply_text(f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country})")

            zone = country_zone_map.get(country)
            if not zone:
                return await update.message.reply_text("❌ الدولة غير مدرجة في قائمة الشحن")

            base, extra = zone_prices[zone]
            total = base if weight <= 0.5 else base + math.ceil((weight - 0.5) / 0.5) * extra
            if country in war_zone_extra and country not in ["فلسطين", "سوريا", "لبنان", "العراق", "تركيا"]:
                total += 15
                return await update.message.reply_text(f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {base} + إضافات حرب + وزن إضافي")

            return await update.message.reply_text(f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {base} + وزن إضافي")

        # إذا كانت عدد قطع → نفس الحساب القديم
        quantity = int(qty_or_weight)
        response = calculate_shipping(country, quantity, season)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# --- تشغيل البوت ---
app = ApplicationBuilder().token(TOKEN).build()

# تحقق من أنه لا يوجد بوت آخر يعمل بنفس الوقت
import os
if "telegram_bot" in os.popen("ps aux").read():
    print("يتم تشغيل بوت آخر. إيقاف البوت الحالي.")
else:
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

