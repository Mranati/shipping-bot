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
    "فلسطين": lambda w, region: (
        11 if region == "الضفة" and w <= 2 else 11 + math.ceil((w - 2) / 0.5) * 5 if region == "الضفة" else
        13 if region == "القدس" and w <= 2 else 13 + math.ceil((w - 2) / 0.5) * 5 if region == "القدس" else
        20 if region == "الداخل" and w <= 2 else 20 + math.ceil((w - 2) / 0.5) * 5),
    "سوريا": lambda w: 35 if w <= 2 else 35 + math.ceil((w - 2) / 0.5) * 12,
    "لبنان": lambda w: 35 if w <= 2 else 35 + math.ceil((w - 2) / 0.5) * 12,
    "العراق": lambda w: 30 if w <= 2 else 30 + math.ceil((w - 2) / 0.5) * 8,
    "تركيا": lambda w: 30 if w <= 2 else 30 + math.ceil((w - 2) / 0.5) * 8
}

# --- دول مناطق الحرب ---
war_zone_extra = ["العراق", "فلسطين", "ليبيا", "اليمن", "سوريا"]

# --- الدول العادية --- 
normal_countries = list(country_zone_map.keys())

# --- دالة مطابقة تقريبية للاسم ---
def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة")  # تصحيح الهاء ↔ التاء المربوطة
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

# --- دالة الحساب ---
def calculate_shipping(country, quantity, season, region=None):
    weight = quantity * (0.5 if season == "صيفية" or season == "صيفي" else 1)

    # تحقق من استثناءات أولاً
    if country in special_cases:
        # إذا كانت فلسطين، نتأكد من المنطقة
        if country == "فلسطين":
            if region not in ["الضفة", "القدس", "الداخل"]:
                return "⚠️ المنطقة غير صحيحة. يرجى اختيار (الضفة، القدس، الداخل)"
            price = special_cases[country](weight, region)
            return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country} - {region})"
        
        # لحساب الأسعار لبقية الدول الاستثنائية
        price = special_cases[country](weight)
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

        if len(parts) != 4:
            await update.message.reply_text("⚠️ يرجى إدخال: الدولة المنطقة عدد القطع/الوزن الموسم (صيفي/شتوي)")
            return

        raw_country, region, qty, season = parts

        # إذا كانت الدولة فلسطين
        if "فلسطين" in raw_country:
            country = "فلسطين"
            region = region  # تحديد المنطقة (الضفة، القدس، الداخل)
            quantity = float(qty)  # استخدام الوزن بدلًا من عدد القطع
        else:
            country = match_country(raw_country, list(country_zone_map.keys()) + list(special_cases.keys()))
            region = None  # باقي الدول لا يحتاجون إلى منطقة
            quantity = int(qty)

        if not country:
            await update.message.reply_text("❌ الدولة غير معروفة")
            return

        if season not in ["صيفية", "شتوية", "صيفي", "شتوي"]:
            await update.message.reply_text("⚠️ نوع القطع يجب أن يكون صيفي/صيفية أو شتوي/شتوية فقط")
            return

        response = calculate_shipping(country, quantity, season, region if country == "فلسطين" else None)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# --- تشغيل البوت ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
