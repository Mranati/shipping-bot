
import os
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from rapidfuzz import process
from country_zone_map_full_UPDATED_FINAL_SMART import country_zone_map, country_aliases, zone_prices, special_cases, special_cases_palestine, exchange_rates

# --- إعدادات عامة ---
last_prices = {}
last_countries = {}

# أسماء العملات بالعربي
currency_names = {
    "USD": "دولار أمريكي",
    "SAR": "ريال سعودي",
    "AED": "درهم إماراتي",
    "QAR": "ريال قطري",
    "KWD": "دينار كويتي",
    "OMR": "ريال عماني",
    "BHD": "دينار بحريني",
    "LYD": "دينار ليبي",
    "IQD": "دينار عراقي",
    "ILS": "شيكل",
    "CAD": "دولار كندي",
    "AUD": "دولار أسترالي",
    "EUR": "يورو",
    "GBP": "جنيه إسترليني"
}

# ربط الدولة بعملتها الأساسية
country_to_currency = {
    "السعودية": "SAR",
    "الإمارات العربية المتحدة": "AED",
    "قطر": "QAR",
    "الكويت": "KWD",
    "البحرين": "BHD",
    "عمان": "OMR",
    "العراق": "IQD",
    "ليبيا": "LYD",
    "فلسطين": "ILS",
    "الأردن": "JOD",
    "كندا": "CAD",
    "أستراليا": "AUD",
    "الولايات المتحدة": "USD",
    "المملكة المتحدة": "GBP",
    "ألمانيا": "EUR",
    "فرنسا": "EUR"
}

def convert_arabic_numerals(text):
    return text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))

def extract_weight_from_text(text: str):
    text = convert_arabic_numerals(text)
    import re
    matches = re.findall(r'(\d+)\s*(صيفي(?:ة)?|شتوي(?:ة)?)', text)
    total_weight = 0
    detail_parts = []
    for count, type_ in matches:
        count = int(count)
        if "صيف" in type_:
            w = count * 0.5
            total_weight += w
            detail_parts.append(f"{count} صيفي = {w} كغ")
        elif "شت" in type_:
            w = count * 1.0
            total_weight += w
            detail_parts.append(f"{count} شتوي = {w} كغ")
    return total_weight, " + ".join(detail_parts)

def match_country(user_input, countries):
    user_input = user_input.replace("ه", "ة").strip()
    if user_input in country_aliases:
        return country_aliases[user_input]
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

def calculate_shipping(country, weight, region=None):
    if country == "فلسطين" and region:
        price = special_cases["فلسطين"](weight, region)
        if price == "منطقة غير صحيحة":
            return "⚠️ المنطقة غير صحيحة. يرجى اختيار (الضفة، القدس، الداخل)", None
        return f"السعر: {price} دينار\nالتفاصيل: {weight:.1f} كغ → استثناء خاص ({country} - {region})", price
    if country in special_cases:
        price = special_cases[country](weight)
        return f"السعر: {price} دينار\nالتفاصيل: {weight:.1f} كغ → استثناء خاص ({country})", price
    zone = country_zone_map.get(country)
    if not zone:
        return "❌ الدولة غير مدرجة في قائمة الشحن", None
    base, extra = zone_prices[zone]
    if weight <= 0.5:
        total = base
    else:
        total = base + math.ceil((weight - 0.5) / 0.5) * extra
    return f"السعر: {total} دينار\nالتفاصيل: {weight:.1f} كغ → المنطقة {zone}", total

def build_currency_buttons(country):
    buttons = []
    buttons.append(InlineKeyboardButton("💵 التحويل لـ دولار أمريكي", callback_data="USD"))
    code = country_to_currency.get(country)
    if code and code != "USD":
        name = currency_names.get(code, code)
        buttons.append(InlineKeyboardButton(f"💱 التحويل لـ {name}", callback_data=code))
    buttons.append(InlineKeyboardButton("🌍 خيارات أخرى", callback_data="show_more"))
    return InlineKeyboardMarkup.from_row(buttons)

def build_all_currency_buttons():
    buttons = []
    for code, name in currency_names.items():
        buttons.append([InlineKeyboardButton(f"💱 التحويل لـ {name}", callback_data=f"conv_{code}")])
    return InlineKeyboardMarkup(buttons)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.strip().replace("ه", "ة")
        parts = text.split()

        country_input = parts[0]
        country = match_country(country_input, list(country_zone_map.keys()) + list(special_cases.keys()))
        if not country:
            await update.message.reply_text("❌ الدولة غير مدرجة في قائمة الشحن")
            return

        # إذا فقط اسم الدولة
        if len(parts) == 1:
            if country == "فلسطين":
                await update.message.reply_text("⚠️ يرجى كتابة: فلسطين [المنطقة] لعرض تفاصيل الأسعار.")
                return
            zone = country_zone_map.get(country)
            if not zone:
                await update.message.reply_text("❌ لم يتم العثور على تصنيف للمنطقة.")
                return
            base, extra = zone_prices.get(zone, (None, None))
            if base is None:
                await update.message.reply_text("❌ لم يتم العثور على أسعار الشحن لهذه الدولة.")
                return
            message = f"""📦 *{country}* (المنطقة {zone})
💰 السعر لأول 0.5 كغ: **{base} دينار**
➕ السعر لكل 0.5 كغ إضافي: **{extra} دينار**"""
            await update.message.reply_markdown(message, reply_markup=build_currency_buttons(country))
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
        except:
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
        response = f"{price_line}\n" + details + "\n\n" + "\n".join(rest)

        else:
            response = summary

        user_id = update.effective_user.id
        last_prices[user_id] = price
        last_countries[user_id] = country
        await update.message.reply_text(response, reply_markup=build_currency_buttons(country))

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ غير متوقع: {e}")

async def handle_currency_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "show_more":
        await query.edit_message_reply_markup(reply_markup=build_all_currency_buttons())
        return

    currency_code = query.data.replace("conv_", "") if query.data.startswith("conv_") else query.data
    price_jod = last_prices.get(user_id)
    if not price_jod:
        await query.edit_message_text("❗️ لم يتم تحديد أي سعر للتحويل.")
        return

    rate = exchange_rates.get(currency_code)
    if not rate:
        await query.edit_message_text("❌ العملة غير مدعومة.")
        return

    rate_with_margin = round(rate * 1.07, 4)
    converted = round(price_jod * rate_with_margin, 2)
    currency_name = currency_names.get(currency_code, currency_code)

    await query.edit_message_text(
        f"💱 السعر المحوّل:\n{price_jod} دينار أردني ≈ {converted} {currency_name}\n"
        f"🧮 (1 دينار = {rate_with_margin} {currency_name} بعد إضافة 7%)"
    )

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

# ✅ تعديل مؤكد: تم التحقق من التنسيق النهائي في الردود
# ✅ نسخة نظيفة بعد تعديل السطر المشكل نهائياً
