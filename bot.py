
import os
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from rapidfuzz import process
from country_zone_map_full import country_zone_map, country_aliases, zone_prices, special_cases, special_cases_palestine, exchange_rates

last_prices = {}

def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة").strip()
    if user_input in country_aliases:
        return country_aliases[user_input]
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

def convert_arabic_numerals(text):
    arabic_to_english = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    return text.translate(arabic_to_english)

def extract_weight_from_text(text):
    text = convert_arabic_numerals(text)
    parts = text.split()
    weight = 0
    summer = 0
    winter = 0
    for i in range(len(parts)):
        part = parts[i]
        if part.isdigit():
            num = int(part)
            if i+1 < len(parts):
                next_word = parts[i+1]
                if "صيف" in next_word:
                    summer += num
                elif "شت" in next_word:
                    winter += num
    weight = summer * 0.5 + winter * 1.0
    if weight > 0:
        return weight, f"تم احتساب الوزن كالتالي:\n{summer} صيفي × 0.5 كغ + {winter} شتوي × 1.0 كغ = {weight} كغ"
    return 0, ""

def calculate_shipping(country, weight, region=None):
    if country == "فلسطين" and region:
        price = special_cases["فلسطين"](weight, region)
        if price == "منطقة غير صحيحة":
            return "⚠️ المنطقة غير صحيحة. يرجى اختيار (الضفة، القدس، الداخل)", None
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country} - {region})", price

    if country in special_cases:
        price = special_cases[country](weight)
        return f"السعر: {price} دينار\nالتفاصيل: {weight} كغ → استثناء خاص ({country})", price

    zone = country_zone_map.get(country)
    if not zone:
        return "❌ الدولة غير مدرجة في قائمة الشحن", None

    base, extra = zone_prices[zone]
    if weight <= 0.5:
        total = base
        calc_detail = f"(حتى 0.5 كغ)"
    else:
        total = base + math.ceil((weight - 0.5) / 0.5) * extra
        calc_detail = f"{base} (أساسي) + {math.ceil((weight - 0.5) / 0.5)} × {extra} (وزن إضافي)"

    return f"السعر: {total} دينار\nالتفاصيل: {weight} كغ → المنطقة {zone} → {calc_detail}", total

def build_currency_keyboard():
    buttons = []
    for code, rate in exchange_rates.items():
        buttons.append([InlineKeyboardButton(code, callback_data=code)])
    return InlineKeyboardMarkup(buttons)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip().replace("ه", "ة")
        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("⚠️ يرجى كتابة: الدولة [الوزن كغ] أو [عدد] [صيفي/شتوي]")
            return

        country_input = parts[0]
        country = match_country(country_input, list(country_zone_map.keys()) + list(special_cases.keys()))
        if not country:
            await update.message.reply_text("❌ الدولة غير مدرجة في قائمة الشحن")
            return

        if country == "فلسطين":
            if len(parts) < 3:
                await update.message.reply_text("⚠️ يرجى كتابة: فلسطين [المنطقة] [الوزن أو عدد القطع]")
                return
            region = parts[1]
            remaining = parts[2:]
        else:
            region = None
            remaining = parts[1:]

        rest_text = " ".join(remaining)
        weight = 0
        details = ""

        try:
            weight = float(convert_arabic_numerals(rest_text.replace("كغ", "").strip()))
        except Exception:
            weight, details = extract_weight_from_text(rest_text)

        if weight == 0:
            await update.message.reply_text("⚠️ لم أتمكن من حساب الوزن من المدخلات.")
            return

        summary, price = calculate_shipping(country, weight, region if country == "فلسطين" else None)
        if not price:
            await update.message.reply_text(summary)
            return

        if details:
            price_line, *rest = summary.splitlines()
            response = f"{price_line}\n{details}\n\n" + "\n".join(rest)
        else:
            response = summary

        last_prices[update.effective_user.id] = price
        await update.message.reply_text(response, reply_markup=build_currency_keyboard())

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ غير متوقع: {e}")

async def handle_currency_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        currency_code = query.data
        if user_id not in last_prices:
            await query.edit_message_text("❗️ لم يتم تحديد أي سعر للتحويل.")
            return
        price_jod = last_prices[user_id]
        rate = exchange_rates.get(currency_code)
        converted = round(price_jod * rate, 2)
        await query.edit_message_text(
            f"💱 السعر المحوّل:\n{price_jod} دينار أردني ≈ {converted} {currency_code}\n🧮 (1 دينار = {rate} {currency_code})"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ أثناء التحويل: {e}")

if __name__ == '__main__':
    TOKEN = os.getenv("TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_currency_selection))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    )
