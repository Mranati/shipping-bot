import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler

from country_zone_map_full import country_zone_map, country_aliases, zone_prices, special_cases, special_cases_palestine, exchange_rates
from shipping_logic import match_country, convert_arabic_numerals, extract_weight_from_text, calculate_shipping

TOKEN = os.getenv("TOKEN")
last_prices = {}

def build_currency_keyboard(preferred=None):
    buttons = []
    buttons.append([InlineKeyboardButton("💲 التحويل لـ دولار أمريكي", callback_data="USD")])

    if preferred and preferred != "USD":
        buttons.append([InlineKeyboardButton(f"💱 التحويل لـ {preferred}", callback_data=preferred)])

    buttons.append([InlineKeyboardButton("🌍 خيارات أخرى", callback_data="more_currencies")])
    return InlineKeyboardMarkup(buttons)

def build_more_currencies_keyboard():
    buttons = []
    for code, name in exchange_rates.items():
        if code != "USD":
            buttons.append([InlineKeyboardButton(f"💱 التحويل لـ {name}", callback_data=code)])
    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="back_to_main")])
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
            response = f"{price_line}
{details}

" + "
".join(rest)
        else:
            response = summary

        last_prices[update.effective_user.id] = price

        currency_hint = {
            "السعودية": "SAR",
            "الإمارات": "AED",
            "قطر": "QAR",
            "الكويت": "KWD",
            "البحرين": "BHD",
            "عمان": "OMR",
            "العراق": "IQD",
            "فلسطين": "ILS",
            "ليبيا": "LYD",
            "أمريكا": "USD",
            "كندا": "CAD",
            "استراليا": "AUD",
            "بريطانيا": "GBP",
            "انجلترا": "GBP",
            "ألمانيا": "EUR",
            "فرنسا": "EUR",
        }
        preferred_currency = currency_hint.get(country)

        await update.message.reply_text(response, reply_markup=build_currency_keyboard(preferred_currency))
    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ غير متوقع: {e}")

async def handle_currency_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        currency_code = query.data

        if currency_code == "more_currencies":
            await query.edit_message_reply_markup(reply_markup=build_more_currencies_keyboard())
            return
        elif currency_code == "back_to_main":
            preferred = None
            for name, code in exchange_rates.items():
                if code == "USD":
                    continue
                if user_id in last_prices:
                    preferred = code
            await query.edit_message_reply_markup(reply_markup=build_currency_keyboard(preferred))
            return

        if user_id not in last_prices:
            await query.edit_message_text("❗️ لم يتم تحديد أي سعر للتحويل.")
            return

        price_jod = last_prices[user_id]
        rate = exchange_rates.get(currency_code)
        converted = round(price_jod * rate, 2)
        await query.edit_message_text(
            f"💱 السعر المحوّل:
{price_jod} دينار أردني ≈ {converted} {currency_code}
🧮 (1 دينار = {rate} {currency_code})"
        )
    except Exception as e:
        await update.callback_query.message.reply_text(f"⚠️ حدث خطأ أثناء التحويل: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_currency_selection))
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/"
    )