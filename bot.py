import math
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from rapidfuzz import process
from country_zone_map_full import country_zone_map

TOKEN = os.getenv("TOKEN")

zone_prices = {
    "1": (12, 5),
    "2": (12, 5),
    "3": (18, 8),
    "4": (19, 8),
    "5": (20, 12),
    "A": (28, 16)
}

special_cases_palestine = {
    "الضفة": lambda w: 11 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 11,
    "القدس": lambda w: 13 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 13,
    "الداخل": lambda w: 20 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 20
}

special_cases = {
    "السعودية": lambda w: 15 + math.ceil((w - 0.5) / 0.5) * 5 if w > 0.5 else 15,
    "فلسطين": lambda w, region: special_cases_palestine.get(region, lambda w: "منطقة غير صحيحة")(w),
    "سوريا": lambda w: 35 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 35,
    "لبنان": lambda w: 35 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 35,
    "العراق": lambda w: 30 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 30,
    "تركيا": lambda w: 30 + math.ceil((w - 2) / 0.5) * 5 if w > 2 else 30
}

def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة")
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

def calculate_shipping(country, quantity, region=None):
    weight = quantity

    if country == "فلسطين" and region:
        price = special_cases["فلسطين"](weight, region)
        if price == "منطقة غير صحيحة":
            return "⚠️ المنطقة غير صحيحة. يرجى اختيار (الضفة، القدس، الداخل)"
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country} - {region})"

    if country in special_cases:
        price = special_cases[country](weight)
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country})"

    zone = country_zone_map.get(country)
    if not zone:
        return "❌ الدولة غير مدرجة في قائمة الشحن"

    base, extra = zone_prices[zone]

    if weight <= 0.5:
        total = base
        breakdown = f"{base} (حتى 0.5 كغ)"
    else:
        extra_units = math.ceil((weight - 0.5) / 0.5)
        extra_cost = extra_units * extra
        total = base + extra_cost
        breakdown = f"{base} (أساسي) + {extra_cost} (وزن إضافي: {extra_units} × {extra})"

    return f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {breakdown}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip()
        parts = text.split()

        if len(parts) < 2:
            await update.message.reply_text("⚠️ يرجى إدخال: الدولة (أو فلسطين المنطقة) الوزن مع وحدة 'كغ'")
            return

        if "فلسطين" in parts[0]:
            if len(parts) < 3:
                await update.message.reply_text("⚠️ يرجى كتابة: فلسطين [المنطقة] [الوزن كغ]")
                return
            country = "فلسطين"
            region = parts[1]
            weight_str = " ".join(parts[2:])
        else:
            country = parts[0]
            region = None
            weight_str = " ".join(parts[1:])

        # معالجة الوزن
        weight_str = weight_str.replace(" ", "").replace("كغ", "")
        try:
            weight = float(weight_str)
        except:
            await update.message.reply_text("⚠️ الوزن غير صالح. يرجى التأكد من كتابة الرقم مع 'كغ'")
            return

        response = calculate_shipping(country, weight, region if country == "فلسطين" else None)
        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# --- تشغيل Webhook ---
if __name__ == '__main__':
    from telegram.ext import Application
    print("🚀 البوت يعمل باستخدام Webhook")

    port = int(os.environ.get("PORT", 8443))
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    )
