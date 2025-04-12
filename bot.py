
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

# أسعار مخصصة للردود فقط لبعض الدول ذات الاستثناء
special_case_responses = {
    "السعودية": "15 دينار لأول 0.5 كغ
5 دينار لكل 0.5 كغ إضافي",
    "سوريا": "35 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي",
    "لبنان": "35 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي",
    "العراق": "30 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي",
    "تركيا": "30 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي",
    "فلسطين": "الضفة: 11 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي
القدس: 13 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي
الداخل: 20 دينار لأول 2 كغ
5 دينار لكل 0.5 كغ إضافي"
}
