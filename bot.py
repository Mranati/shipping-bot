import math
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from rapidfuzz import process

# استيراد قائمة الدول من الملف الخارجي
from country_zone_map_full import country_zone_map

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

# --- استثناءات فلسطين ---
special_cases_palestine = {
    "الضفة": lambda w: 11 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 11,
    "القدس": lambda w: 13 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 13,
    "الداخل": lambda w: 20 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 20
}

# --- استثناءات الدول الأخرى ---
special_cases = {
    "السعودية": lambda w: 15 + math.ceil((w - 0.5) / 0.5) * 5 if w > 0.5 else 15,
    "فلسطين": lambda w, region: special_cases_palestine.get(region, lambda w: "منطقة غير صحيحة")(w),
    "سوريا": lambda w: 35 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 35,
    "لبنان": lambda w: 35 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 35,
    "العراق": lambda w: 30 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 30,
    "تركيا": lambda w: 30 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 30
}

# --- دول أخرى ---
country_zone_map = country_zone_map  # استيراد قائمة البلدان من الملف الخارجي

# --- دالة مطابقة تقريبية للاسم ---
def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة")  # تصحيح الهاء ↔ التاء المربوطة
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

# --- دالة حساب السعر ---
def calculate_shipping(country, quantity, region=None):
    weight = quantity  # الوزن يتم تحديده مباشرة من المدخلات بدون الحاجة للموسم أو القطع

    # التحقق من استثناءات فلسطين
    if country == "فلسطين" and region:
        # حساب السعر بناءً على المنطقة فقط
        price = special_cases["فلسطين"](weight, region)
        if price == "منطقة غير صحيحة":
            return "⚠️ المنطقة غير صحيحة. يرجى اختيار (الضفة، القدس، الداخل)"
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country} - {region})"
    
    # التحقق من استثناءات الدول الأخرى
    if country in special_cases:
        price = special_cases[country](weight)
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country})"

    # منطقة الدولة (في حالة الدول العادية)
    zone = country_zone_map.get(country)
    if not zone:
        return "❌ الدولة غير مدرجة في قائمة الشحن"

    base, extra = zone_prices[zone]
    if weight <= 0.5:
        total = base
    else:
        total = base + math.ceil((weight - 0.5) / 0.5) * extra

    return f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {base} + وزن إضافي"

# --- الرد على الرسائل ---  
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) < 3:
            await update.message.reply_text("⚠️ يرجى إدخال: الدولة (أو فلسطين المنطقة) الوزن مع وحدة 'كغ'")
            return
        
        # التحقق إذا كانت المدخلات تخص فلسطين
        if "فلسطين" in parts[0]:
            # التعامل مع فلسطين مع مسافة بين الوزن وكغ
            weight_part = parts[2]
            if "كغ" not in weight_part:
                await update.message.reply_text("⚠️ الوزن يجب أن يكون مع 'كغ' مع مسافة بين الوزن وكغ.")
                return
            weight = float(weight_part.replace("كغ", "").strip())
            country = "فلسطين"
            region = parts[1]
        else:
            # التعامل مع باقي الدول مع مسافة بين الوزن وكغ
            country = parts[0]
            region = None
            weight_part = parts[1]
            if "كغ" not in weight_part:
                await update.message.reply_text("⚠️ الوزن يجب أن يكون مع 'كغ' مع مسافة بين الوزن وكغ.")
                return
            weight = float(weight_part.replace("كغ", "").strip())

        # حساب السعر بناءً على المدخلات
        response = calculate_shipping(country, weight, region if country == "فلسطين" else None)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# --- تشغيل البوت ---
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

if __name__ == '__main__':
    app.run_polling()
