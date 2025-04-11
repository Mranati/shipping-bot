
import math
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from rapidfuzz import process
from country_zone_map_full_UPDATED import country_zone_map

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

country_aliases = {
    "امريكا": "الولايات المتحدة",
    "أمريكا": "الولايات المتحدة",
    "انجلترا": "المملكة المتحدة",
    "إنجلترا": "المملكة المتحدة",
    "بريطانيا": "المملكة المتحدة",
    "روسيا": "الاتحاد الروسي",
    "كوريا الجنوبية": "جمهورية كوريا",
    "كوريا الشمالية": "جمهورية كوريا الشعبية الديمقراطية",
    "المانيا": "ألمانيا",
    "هولندا": "هولندا",
    "النيذرلاندز": "هولندا",
    "التشيك": "جمهورية التشيك",
    "سلوفاكيا": "الجمهورية السلوفاكية",
    "اليونان": "جمهورية اليونان",
    "الصين": "جمهورية الصين الشعبية",
    "تايوان": "تايوان، مقاطعة الصين",
    "الكونغو": "جمهورية الكونغو",
    "الكونغو الديمقراطية": "جمهورية الكونغو الديمقراطية",
    "الامارات": "الإمارات العربية المتحدة",
    "السودان الجنوبي": "جنوب السودان",
    "كوريا": "جمهورية كوريا",
    "فنزويلا": "جمهورية فنزويلا البوليفارية",
    "ساحل العاج": "كوت ديفوار",
    "كندا": "كندا",
    "مصر": "مصر",
    "الاردن": "الأردن",
    "اسرائيل": "إسرائيل",
    "نيوزيلندا": "نيوزيلندا",
}

def convert_arabic_numerals(text):
    return text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))

def extract_weight_from_text(text: str):
    text = convert_arabic_numerals(text)
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
    user_input = user_input.replace("ه", "ة")
    if user_input in country_aliases:
        return country_aliases[user_input]
    result = process.extractOne(user_input, countries)
    return result[0] if result and result[1] >= 80 else None

def calculate_shipping(country, weight, region=None):
    if country == "فلسطين" and region:
        price = special_cases["فلسطين"](weight, region)
        if price == "منطقة غير صحيحة":
            return "⚠️ المنطقة غير صحيحة. يرجى اختيار (الضفة، القدس، الداخل)"
        return f"السعر: {price} دينار\nالتفاصيل: {weight:.1f} كغ → استثناء خاص ({country} - {region})"
    if country in special_cases:
        price = special_cases[country](weight)
        return f"السعر: {price} دينار\nالتفاصيل: {weight:.1f} كغ → استثناء خاص ({country})"
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
    return f"السعر: {total} دينار\nالتفاصيل: {weight:.1f} كغ → المنطقة {zone} → {breakdown}"

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
        weight = None
        details = ""
        try:
            weight = float(convert_arabic_numerals(rest_text.replace("كغ", "").strip()))
        except:
            weight, details = extract_weight_from_text(rest_text)
        if weight == 0:
            await update.message.reply_text("⚠️ لم أتمكن من حساب الوزن من المدخلات.")
            return
        summary = calculate_shipping(country, weight, region if country == "فلسطين" else None)
        if details:
            price_line, *rest = summary.splitlines()
            response = f"{price_line}\n{details}\n\n" + "\n".join(rest)
        else:
            response = summary
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ غير متوقع: {e}")

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
