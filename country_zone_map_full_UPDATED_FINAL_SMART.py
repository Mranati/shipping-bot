import math
country_zone_map = {
    "أبخازيا": "5",
    "أفغانستان": "5",
    "ألبانيا": "5",
    "الجزائر": "A",
    "ساموا الأمريكية": "5",
    "أندورا": "5",
    "أنغولا": "4",
    "أنغيلا": "5",
    "أنتاركتيكا": "5",
    "أنتيغوا وبربودا": "5",
    "الأرجنتين": "5",
    "أرمينيا": "5",
    "أروبا": "5",
    "جزر أسنسيون": "A",
    "أستراليا": "4",
    "النمسا": "4",
    "أذربيجان": "5",
    "جزر الأزور": "A",
    "الباهاما": "A",
    "البحرين": "2",
    "بنغلاديش": "2",
    "بربادوس": "A",
    "بيلاروس": "5",
    "بلجيكا": "3",
    "بليز": "A",
    "بنين": "5",
    "برمودا": "A",
    "بوتان": "5",
    "بوليفيا": "5",
    "البوسنة والهرسك": "5",
    "بوتسوانا": "5",
    "جزيرة بوفيه": "A",
    "البرازيل": "5",
    "بروناي": "5",
    "بلغاريا": "5",
    "بوركينا فاسو": "5",
    "بورما": "5",
    "بوروندي": "5",
    "كمبوديا": "5",
    "الكاميرون": "5",
    "كندا": "4",
    "جزر الكناري": "5",
    "الرأس الأخضر": "A",
    "جزر كايمان": "A",
    "جمهورية أفريقيا الوسطى": "5",
    "تشاد": "5",
    "جزر القنال": "A",
    "تشيلي": "5",
    "الصين": "4",
    "جزيرة الكريسماس": "A",
    "جزر كوكوس": "A",
    "كولومبيا": "5",
    "جزر القمر": "A",
    "الكونغو": "5",
    "جزر كوك": "A",
    "كوستاريكا": "5",
    "ساحل العاج": "5",
    "كرواتيا": "5",
    "كوبا": "5",
    "قبرص": "3",
    "جمهورية التشيك": "5",
    "الدانمارك": "3",
    "جيبوتي": "5",
    "دومينيكا": "A",
    "جمهورية الدومينيكان": "A",
    "تيمور الشرقية": "A",
    "الإكوادور": "5",
    "مصر": "2",
    "السلفادور": "5",
    "غينيا الاستوائية": "5",
    "إريتريا": "5",
    "إستونيا": "5",
    "إثيوبيا": "5",
    "جزر فوكلاند": "A",
    "جزر فارو": "A",
    "فيجي": "5",
    "فنلندا": "3",
    "فرنسا": "3",
    "غويانا الفرنسية": "A",
    "بولينيزيا الفرنسية": "5",
    "الغابون": "5",
    "غامبيا": "5",
    "جورجيا": "5",
    "ألمانيا": "3",
    "غانا": "5",
    "جبل طارق": "5",
    "اليونان": "5",
    "جرينلاند": "5",
    "غرينادا": "A",
    "جوادلوب": "A",
    "غوام": "5",
    "غواتيمالا": "5",
    "غيرنزي": "A",
    "غينيا": "5",
    "غينيا-بيساو": "5",
    "غيانا": "5",
    "هايتي": "A",
    "هندوراس": "5",
    "هونغ كونغ": "4",
    "هنغاريا": "5",
    "آيسلندا": "5",
    "الهند": "2",
    "إندونيسيا": "4",
    "إيران": "3",
    "العراق": "3",
    "إيرلندا": "3",
    "جزيرة مان": "A",
    "إسرائيل": "3",
    "إيطاليا": "3",
    "جامايكا": "5",
    "اليابان": "5",
    "جيرسي": "A",
    "الأردن": "2",
    "كازاخستان": "3",
    "كينيا": "4",
    "كيريباتي": "A",
    "كوريا الشمالية": "5",
    "كوريا الجنوبية": "5",
    "كوسوفو": "5",
    "الكويت": "2",
    "قيرغيزستان": "5",
    "لاوس": "5",
    "لاتفيا": "5",
    "لبنان": "1",
    "ليسوتو": "5",
    "ليبيريا": "5",
    "ليبيا": "5",
    "ليختنشتاين": "5",
    "ليتوانيا": "5",
    "لوكسمبورغ": "4",
    "ماكاو": "5",
    "مقدونيا": "5",
    "مدغشقر": "5",
    "جزر ماديرا": "5",
    "مالاوي": "5",
    "ماليزيا": "4",
    "المالديف": "5",
    "مالي": "5",
    "مالطا": "4",
    "جزر مارشال": "A",
    "مارتينيك": "A",
    "موريتانيا": "5",
    "موريشيوس": "5",
    "مايوت": "A",
    "المكسيك": "5",
    "ميكرونيزيا": "A",
    "مولدوفا": "5",
    "موناكو": "3",
    "منغوليا": "5",
    "الجبل الأسود": "5",
    "مونتسيرات": "A",
    "المغرب": "3",
    "موزمبيق": "5",
    "ميانمار": "5",
    "ناميبيا": "5",
    "ناورو": "A",
    "نيبال": "4",
    "هولندا": "4",
    "جزر الأنتيل الهولندية": "5",
    "كاليدونيا الجديدة": "A",
    "نيوزيلندا": "4",
    "نيكاراغوا": "5",
    "النيجر": "5",
    "نيجيريا": "5",
    "جزيرة نورفولك": "A",
    "أيرلندا الشمالية": "5",
    "جزر ماريانا الشمالية": "A",
    "النرويج": "4",
    "عمان": "2",
    "باكستان": "2",
    "بالاو": "A",
    "فلسطين": "1",
    "بنما": "5",
    "بابوا غينيا الجديدة": "5",
    "باراغواي": "5",
    "بيرو": "5",
    "الفلبين": "4",
    "جزر بيتكيرن": "A",
    "بولندا": "5",
    "البرتغال": "3",
    "بورتو ريكو": "5",
    "قطر": "2",
    "ريونيون": "A",
    "رومانيا": "5",
    "روسيا": "5",
    "رواندا": "5",
    "ساموا": "5",
    "سان مارينو": "5",
    "ساو تومي وبرينسيب": "A",
    "السعودية": "2",
    "اسكتلندا": "5",
    "السنغال": "5",
    "صربيا": "5",
    "سيشيل": "5",
    "سيراليون": "5",
    "سنغافورة": "4",
    "سلوفاكيا": "5",
    "سلوفينيا": "5",
    "جزر سليمان": "A",
    "الصومال": "5",
    "جنوب أفريقيا": "5",
    "جورجيا الجنوبية": "5",
    "جنوب السودان": "5",
    "إسبانيا": "5",
    "سريلانكا": "3",
    "سانت هيلينا": "A",
    "سانت كيتس ونيفيس": "A",
    "سانت لوسيا": "A",
    "سانت بيير وميكلون": "A",
    "سانت فنسنت والغرينادين": "A",
    "السودان": "3",
    "سورينام": "A",
    "سفالبارد ويان ماين": "A",
    "إسواتيني": "5",
    "السويد": "3",
    "سويسرا": "3",
    "سوريا": "1",
    "تايوان": "4",
    "طاجيكستان": "5",
    "تنزانيا": "5",
    "تايلاند": "4",
    "توغو": "5",
    "تونغا": "5",
    "ترينيداد وتوباغو": "A",
    "تونس": "A",
    "تركيا": "3",
    "تركمانستان": "5",
    "جزر تركس وكايكوس": "A",
    "توفالو": "A",
    "أوغندا": "5",
    "أوكرانيا": "5",
    "الإمارات": "2",
    "المملكة المتحدة": "3",
    "الولايات المتحدة": "4",
    "أوروغواي": "5",
    "أوزبكستان": "3",
    "فانواتو": "A",
    "مدينة الفاتيكان": "5",
    "فنزويلا": "5",
    "فيتنام": "5",
    "جزر العذراء البريطانية": "A",
    "جزر العذراء الأمريكية": "A",
    "ويلز": "5",
    "جزر واليس وفوتونا": "A",
    "الصحراء الغربية": "A",
    "اليمن": "3",
    "امريكا": "4",
    "أمريكا": "4",
    "انجلترا": "3",
    "إنجلترا": "3",
    "بريطانيا": "3",
    "المانيا": "3",
    "النيذرلاندز": "4",
    "التشيك": "5",
    "السودان الجنوبي": "5",
    "الاردن": "2",
    "اسرائيل": "3"
}

country_aliases = {
    "امريكا": "الولايات المتحدة",
    "أمريكا": "الولايات المتحدة",
    "انجلترا": "المملكة المتحدة",
    "إنجلترا": "المملكة المتحدة",
    "بريطانيا": "المملكة المتحدة",
    "روسيا": "روسيا",
    "كوريا": "كوريا الجنوبية",
    "كوريا الجنوبية": "كوريا الجنوبية",
    "كوريا الشمالية": "كوريا الشمالية",
    "المانيا": "ألمانيا",
    "هولندا": "هولندا",
    "النيذرلاندز": "هولندا",
    "الامارات": "الإمارات العربية المتحدة",
    "الإمارات": "الإمارات العربية المتحدة",
    "السعوديه": "السعودية",
    "الكويت": "الكويت",
    "قطر": "قطر",
    "عُمان": "عمان",
    "العراق": "العراق",
    "لبنان": "لبنان",
    "الأردن": "الأردن",
    "مصر": "مصر",
    "تركيا": "تركيا",
    "فلسطين": "فلسطين",
    "الضفة": "فلسطين",
    "الداخل": "فلسطين",
    "القدس": "فلسطين",
    "نيوزلندا": "نيوزيلندا",
    "استراليا": "أستراليا"
}


zone_prices = {
    "1": (12, 5),
    "2": (12, 5),
    "3": (18, 8),
    "4": (19, 8),
    "5": (20, 12),
    "A": (28, 16)
}


special_cases_palestine = {
    "الضفة": lambda w: 11 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 11,
    "القدس": lambda w: 13 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 13,
    "الداخل": lambda w: 20 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 20
}


special_cases = {
    "السعودية": lambda w: 15 + math.ceil((w - 0.5) / 0.5) * 5 if w > 0.5 else 15
    "فلسطين": lambda w, region: special_cases_palestine.get(region, lambda w: "منطقة غير صحيحة")(w),
    "سوريا": lambda w: 35 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 35,
    "لبنان": lambda w: 35 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 35,
    "العراق": lambda w: 30 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 30,
    "تركيا": lambda w: 30 + ((w - 2) // 0.5 + 1) * 5 if w > 2 else 30
}


exchange_rates = {
    "USD": 1.41,
    "SAR": 5.03,
    "AED": 5.17,
    "QAR": 5.15,
    "KWD": 0.43,
    "OMR": 0.53,
    "BHD": 0.53,
    "LYD": 6.75,
    "IQD": 1990,
    "ILS": 5.00,
    "CAD": 1.91,
    "AUD": 2.10,
    "EUR": 1.29,
    "GBP": 1.11
}


country_aliases = {
    "أرجنتين": "الأرجنتين",
    "أردن": "الأردن",
    "أيرلندا الشماليه": "أيرلندا الشمالية",
    "إكوادور": "الإكوادور",
    "إمارات": "الإمارات",
    "ابخازيا": "أبخازيا",
    "اثيوبيا": "إثيوبيا",
    "اذربيجان": "أذربيجان",
    "ارجنتين": "الأرجنتين",
    "اردن": "الاردن",
    "ارمينيا": "أرمينيا",
    "اروبا": "أروبا",
    "اريتريا": "إريتريا",
    "اسبانيا": "إسبانيا",
    "استراليا": "أستراليا",
    "استونيا": "إستونيا",
    "اسواتيني": "إسواتيني",
    "افغانستان": "أفغانستان",
    "اكوادور": "الإكوادور",
    "الآيسلندا": "آيسلندا",
    "الأبخازيا": "أبخازيا",
    "الأذربيجان": "أذربيجان",
    "الأرمينيا": "أرمينيا",
    "الأروبا": "أروبا",
    "الأستراليا": "أستراليا",
    "الأفغانستان": "أفغانستان",
    "الألبانيا": "ألبانيا",
    "الألمانيا": "ألمانيا",
    "الأمريكا": "أمريكا",
    "الأنتاركتيكا": "أنتاركتيكا",
    "الأنتيغوا وبربودا": "أنتيغوا وبربودا",
    "الأندورا": "أندورا",
    "الأنغولا": "أنغولا",
    "الأنغيلا": "أنغيلا",
    "الأوروغواي": "أوروغواي",
    "الأوزبكستان": "أوزبكستان",
    "الأوغندا": "أوغندا",
    "الأوكرانيا": "أوكرانيا",
    "الأيرلندا الشمالية": "أيرلندا الشمالية",
    "الأيرلندا الشماليه": "أيرلندا الشمالية",
    "الإثيوبيا": "إثيوبيا",
    "الإريتريا": "إريتريا",
    "الإسبانيا": "إسبانيا",
    "الإستونيا": "إستونيا",
    "الإسرائيل": "إسرائيل",
    "الإسواتيني": "إسواتيني",
    "الإنجلترا": "إنجلترا",
    "الإندونيسيا": "إندونيسيا",
    "الإيران": "إيران",
    "الإيرلندا": "إيرلندا",
    "الإيطاليا": "إيطاليا",
    "الابخازيا": "أبخازيا",
    "الاثيوبيا": "إثيوبيا",
    "الاذربيجان": "أذربيجان",
    "الارجنتين": "الأرجنتين",
    "الارمينيا": "أرمينيا",
    "الاروبا": "أروبا",
    "الاريتريا": "إريتريا",
    "الاسبانيا": "إسبانيا",
    "الاستراليا": "أستراليا",
    "الاستونيا": "إستونيا",
    "الاسرائيل": "اسرائيل",
    "الاسكتلندا": "اسكتلندا",
    "الاسواتيني": "إسواتيني",
    "الافغانستان": "أفغانستان",
    "الاكوادور": "الإكوادور",
    "الامارات": "الإمارات",
    "الامريكا": "امريكا",
    "الانتاركتيكا": "أنتاركتيكا",
    "الانتيغوا وبربودا": "أنتيغوا وبربودا",
    "الانجلترا": "إنجلترا",
    "الاندورا": "أندورا",
    "الاندونيسيا": "إندونيسيا",
    "الانغولا": "أنغولا",
    "الانغيلا": "أنغيلا",
    "الاوروغواي": "أوروغواي",
    "الاوزبكستان": "أوزبكستان",
    "الاوغندا": "أوغندا",
    "الاوكرانيا": "أوكرانيا",
    "الايران": "إيران",
    "الايرلندا": "إيرلندا",
    "الايرلندا الشمالية": "أيرلندا الشمالية",
    "الايرلندا الشماليه": "أيرلندا الشمالية",
    "الايسلندا": "آيسلندا",
    "الايطاليا": "إيطاليا",
    "البابوا غينيا الجديدة": "بابوا غينيا الجديدة",
    "البابوا غينيا الجديده": "بابوا غينيا الجديدة",
    "الباةاما": "الباهاما",
    "الباراغواي": "باراغواي",
    "الباكستان": "باكستان",
    "البالاو": "بالاو",
    "البانيا": "ألبانيا",
    "البربادوس": "بربادوس",
    "البرمودا": "برمودا",
    "البروناي": "بروناي",
    "البريطانيا": "بريطانيا",
    "البلجيكا": "بلجيكا",
    "البلغاريا": "بلغاريا",
    "البليز": "بليز",
    "البنغلاديش": "بنغلاديش",
    "البنما": "بنما",
    "البنين": "بنين",
    "البوتان": "بوتان",
    "البوتسوانا": "بوتسوانا",
    "البورتو ريكو": "بورتو ريكو",
    "البوركينا فاسو": "بوركينا فاسو",
    "البورما": "بورما",
    "البوروندي": "بوروندي",
    "البوسنة والةرسك": "البوسنة والهرسك",
    "البوسنه والهرسك": "البوسنة والهرسك",
    "البولندا": "بولندا",
    "البوليفيا": "بوليفيا",
    "البولينيزيا الفرنسية": "بولينيزيا الفرنسية",
    "البولينيزيا الفرنسيه": "بولينيزيا الفرنسية",
    "البيرو": "بيرو",
    "البيلاروس": "بيلاروس",
    "الةايتي": "هايتي",
    "الةند": "الهند",
    "الةندوراس": "هندوراس",
    "الةنغاريا": "هنغاريا",
    "الةولندا": "هولندا",
    "الةونغ كونغ": "هونغ كونغ",
    "التايلاند": "تايلاند",
    "التايوان": "تايوان",
    "التركمانستان": "تركمانستان",
    "التركيا": "تركيا",
    "الترينيداد وتوباغو": "ترينيداد وتوباغو",
    "التشاد": "تشاد",
    "التشيلي": "تشيلي",
    "التنزانيا": "تنزانيا",
    "التوغو": "توغو",
    "التوفالو": "توفالو",
    "التونس": "تونس",
    "التونغا": "تونغا",
    "التيمور الشرقية": "تيمور الشرقية",
    "التيمور الشرقيه": "تيمور الشرقية",
    "الجامايكا": "جامايكا",
    "الجبل الاسود": "الجبل الأسود",
    "الجبل طارق": "جبل طارق",
    "الجرينلاند": "جرينلاند",
    "الجزر أسنسيون": "جزر أسنسيون",
    "الجزر اسنسيون": "جزر أسنسيون",
    "الجزر الأزور": "جزر الأزور",
    "الجزر الأنتيل الةولندية": "جزر الأنتيل الهولندية",
    "الجزر الأنتيل الهولندية": "جزر الأنتيل الهولندية",
    "الجزر الأنتيل الهولنديه": "جزر الأنتيل الهولندية",
    "الجزر الازور": "جزر الأزور",
    "الجزر الانتيل الةولندية": "جزر الأنتيل الهولندية",
    "الجزر الانتيل الهولندية": "جزر الأنتيل الهولندية",
    "الجزر الانتيل الهولنديه": "جزر الأنتيل الهولندية",
    "الجزر العذراء الأمريكية": "جزر العذراء الأمريكية",
    "الجزر العذراء الأمريكيه": "جزر العذراء الأمريكية",
    "الجزر العذراء الامريكية": "جزر العذراء الأمريكية",
    "الجزر العذراء الامريكيه": "جزر العذراء الأمريكية",
    "الجزر العذراء البريطانية": "جزر العذراء البريطانية",
    "الجزر العذراء البريطانيه": "جزر العذراء البريطانية",
    "الجزر القمر": "جزر القمر",
    "الجزر القنال": "جزر القنال",
    "الجزر الكناري": "جزر الكناري",
    "الجزر بيتكيرن": "جزر بيتكيرن",
    "الجزر تركس وكايكوس": "جزر تركس وكايكوس",
    "الجزر سليمان": "جزر سليمان",
    "الجزر فارو": "جزر فارو",
    "الجزر فوكلاند": "جزر فوكلاند",
    "الجزر كايمان": "جزر كايمان",
    "الجزر كوك": "جزر كوك",
    "الجزر كوكوس": "جزر كوكوس",
    "الجزر ماديرا": "جزر ماديرا",
    "الجزر مارشال": "جزر مارشال",
    "الجزر ماريانا الشمالية": "جزر ماريانا الشمالية",
    "الجزر ماريانا الشماليه": "جزر ماريانا الشمالية",
    "الجزر واليس وفوتونا": "جزر واليس وفوتونا",
    "الجزيرة الكريسماس": "جزيرة الكريسماس",
    "الجزيرة بوفية": "جزيرة بوفيه",
    "الجزيرة بوفيه": "جزيرة بوفيه",
    "الجزيرة مان": "جزيرة مان",
    "الجزيرة نورفولك": "جزيرة نورفولك",
    "الجزيره الكريسماس": "جزيرة الكريسماس",
    "الجزيره بوفيه": "جزيرة بوفيه",
    "الجزيره مان": "جزيرة مان",
    "الجزيره نورفولك": "جزيرة نورفولك",
    "الجمةورية أفريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "الجمةورية افريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "الجمةورية التشيك": "جمهورية التشيك",
    "الجمةورية الدومينيكان": "جمهورية الدومينيكان",
    "الجمهورية أفريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "الجمهورية افريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "الجمهورية التشيك": "جمهورية التشيك",
    "الجمهورية الدومينيكان": "جمهورية الدومينيكان",
    "الجمهوريه أفريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "الجمهوريه افريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "الجمهوريه التشيك": "جمهورية التشيك",
    "الجمهوريه الدومينيكان": "جمهورية الدومينيكان",
    "الجنوب أفريقيا": "جنوب أفريقيا",
    "الجنوب افريقيا": "جنوب أفريقيا",
    "الجنوب السودان": "جنوب السودان",
    "الجوادلوب": "جوادلوب",
    "الجورجيا": "جورجيا",
    "الجورجيا الجنوبية": "جورجيا الجنوبية",
    "الجورجيا الجنوبيه": "جورجيا الجنوبية",
    "الجيبوتي": "جيبوتي",
    "الجيرسي": "جيرسي",
    "الدومينيكا": "دومينيكا",
    "الراس الاخضر": "الرأس الأخضر",
    "الرواندا": "رواندا",
    "الروسيا": "روسيا",
    "الرومانيا": "رومانيا",
    "الريونيون": "ريونيون",
    "الساحل العاج": "ساحل العاج",
    "الساموا": "ساموا",
    "الساموا الأمريكية": "ساموا الأمريكية",
    "الساموا الأمريكيه": "ساموا الأمريكية",
    "الساموا الامريكية": "ساموا الأمريكية",
    "الساموا الامريكيه": "ساموا الأمريكية",
    "السان مارينو": "سان مارينو",
    "السانت بيير وميكلون": "سانت بيير وميكلون",
    "السانت ةيلينا": "سانت هيلينا",
    "السانت فنسنت والغرينادين": "سانت فنسنت والغرينادين",
    "السانت كيتس ونيفيس": "سانت كيتس ونيفيس",
    "السانت لوسيا": "سانت لوسيا",
    "السانت هيلينا": "سانت هيلينا",
    "الساو تومي وبرينسيب": "ساو تومي وبرينسيب",
    "السريلانكا": "سريلانكا",
    "السعوديه": "السعودية",
    "السفالبارد ويان ماين": "سفالبارد ويان ماين",
    "السلوفاكيا": "سلوفاكيا",
    "السلوفينيا": "سلوفينيا",
    "السنغافورة": "سنغافورة",
    "السنغافوره": "سنغافورة",
    "السوريا": "سوريا",
    "السورينام": "سورينام",
    "السويسرا": "سويسرا",
    "السيراليون": "سيراليون",
    "السيشيل": "سيشيل",
    "الصحراء الغربيه": "الصحراء الغربية",
    "الصربيا": "صربيا",
    "الطاجيكستان": "طاجيكستان",
    "العمان": "عمان",
    "الغامبيا": "غامبيا",
    "الغانا": "غانا",
    "الغرينادا": "غرينادا",
    "الغواتيمالا": "غواتيمالا",
    "الغوام": "غوام",
    "الغويانا الفرنسية": "غويانا الفرنسية",
    "الغويانا الفرنسيه": "غويانا الفرنسية",
    "الغيانا": "غيانا",
    "الغيرنزي": "غيرنزي",
    "الغينيا": "غينيا",
    "الغينيا الاستوائية": "غينيا الاستوائية",
    "الغينيا الاستوائيه": "غينيا الاستوائية",
    "الغينيا-بيساو": "غينيا-بيساو",
    "الفانواتو": "فانواتو",
    "الفرنسا": "فرنسا",
    "الفلسطين": "فلسطين",
    "الفنزويلا": "فنزويلا",
    "الفنلندا": "فنلندا",
    "الفيتنام": "فيتنام",
    "الفيجي": "فيجي",
    "القبرص": "قبرص",
    "القطر": "قطر",
    "القيرغيزستان": "قيرغيزستان",
    "الكازاخستان": "كازاخستان",
    "الكاليدونيا الجديدة": "كاليدونيا الجديدة",
    "الكاليدونيا الجديده": "كاليدونيا الجديدة",
    "الكرواتيا": "كرواتيا",
    "الكمبوديا": "كمبوديا",
    "الكندا": "كندا",
    "الكوبا": "كوبا",
    "الكوريا الجنوبية": "كوريا الجنوبية",
    "الكوريا الجنوبيه": "كوريا الجنوبية",
    "الكوريا الشمالية": "كوريا الشمالية",
    "الكوريا الشماليه": "كوريا الشمالية",
    "الكوستاريكا": "كوستاريكا",
    "الكوسوفو": "كوسوفو",
    "الكولومبيا": "كولومبيا",
    "الكيريباتي": "كيريباتي",
    "الكينيا": "كينيا",
    "اللاتفيا": "لاتفيا",
    "اللاوس": "لاوس",
    "اللبنان": "لبنان",
    "اللوكسمبورغ": "لوكسمبورغ",
    "الليبيا": "ليبيا",
    "الليبيريا": "ليبيريا",
    "الليتوانيا": "ليتوانيا",
    "الليختنشتاين": "ليختنشتاين",
    "الليسوتو": "ليسوتو",
    "المارتينيك": "مارتينيك",
    "الماكاو": "ماكاو",
    "المالاوي": "مالاوي",
    "المالطا": "مالطا",
    "المالي": "مالي",
    "الماليزيا": "ماليزيا",
    "المايوت": "مايوت",
    "المدغشقر": "مدغشقر",
    "المدينة الفاتيكان": "مدينة الفاتيكان",
    "المدينه الفاتيكان": "مدينة الفاتيكان",
    "المصر": "مصر",
    "المقدونيا": "مقدونيا",
    "المملكه المتحده": "المملكة المتحدة",
    "المنغوليا": "منغوليا",
    "الموريتانيا": "موريتانيا",
    "الموريشيوس": "موريشيوس",
    "الموزمبيق": "موزمبيق",
    "المولدوفا": "مولدوفا",
    "الموناكو": "موناكو",
    "المونتسيرات": "مونتسيرات",
    "الميانمار": "ميانمار",
    "الميكرونيزيا": "ميكرونيزيا",
    "الناميبيا": "ناميبيا",
    "الناورو": "ناورو",
    "النيبال": "نيبال",
    "النيجيريا": "نيجيريا",
    "النيكاراغوا": "نيكاراغوا",
    "النيوزيلندا": "نيوزيلندا",
    "الهايتي": "هايتي",
    "الهندوراس": "هندوراس",
    "الهنغاريا": "هنغاريا",
    "الهولندا": "هولندا",
    "الهونغ كونغ": "هونغ كونغ",
    "الولايات المتحده": "الولايات المتحدة",
    "الويلز": "ويلز",
    "امارات": "الإمارات",
    "انتاركتيكا": "أنتاركتيكا",
    "انتيغوا وبربودا": "أنتيغوا وبربودا",
    "اندورا": "أندورا",
    "اندونيسيا": "إندونيسيا",
    "انغولا": "أنغولا",
    "انغيلا": "أنغيلا",
    "اوروغواي": "أوروغواي",
    "اوزبكستان": "أوزبكستان",
    "اوغندا": "أوغندا",
    "اوكرانيا": "أوكرانيا",
    "ايران": "إيران",
    "ايرلندا": "إيرلندا",
    "ايرلندا الشمالية": "أيرلندا الشمالية",
    "ايرلندا الشماليه": "أيرلندا الشمالية",
    "ايسلندا": "آيسلندا",
    "ايطاليا": "إيطاليا",
    "بابوا غينيا الجديده": "بابوا غينيا الجديدة",
    "باةاما": "الباهاما",
    "بانيا": "ألبانيا",
    "باهاما": "الباهاما",
    "بحرين": "البحرين",
    "برازيل": "البرازيل",
    "برتغال": "البرتغال",
    "بوسنة والةرسك": "البوسنة والهرسك",
    "بوسنة والهرسك": "البوسنة والهرسك",
    "بوسنه والهرسك": "البوسنة والهرسك",
    "بولينيزيا الفرنسيه": "بولينيزيا الفرنسية",
    "ةايتي": "هايتي",
    "ةند": "الهند",
    "ةندوراس": "هندوراس",
    "ةنغاريا": "هنغاريا",
    "ةولندا": "هولندا",
    "ةونغ كونغ": "هونغ كونغ",
    "تشيك": "التشيك",
    "تيمور الشرقيه": "تيمور الشرقية",
    "جبل الأسود": "الجبل الأسود",
    "جبل الاسود": "الجبل الأسود",
    "جزائر": "الجزائر",
    "جزر اسنسيون": "جزر أسنسيون",
    "جزر الأنتيل الةولندية": "جزر الأنتيل الهولندية",
    "جزر الأنتيل الهولنديه": "جزر الأنتيل الهولندية",
    "جزر الازور": "جزر الأزور",
    "جزر الانتيل الةولندية": "جزر الأنتيل الهولندية",
    "جزر الانتيل الهولندية": "جزر الأنتيل الهولندية",
    "جزر الانتيل الهولنديه": "جزر الأنتيل الهولندية",
    "جزر العذراء الأمريكيه": "جزر العذراء الأمريكية",
    "جزر العذراء الامريكية": "جزر العذراء الأمريكية",
    "جزر العذراء الامريكيه": "جزر العذراء الأمريكية",
    "جزر العذراء البريطانيه": "جزر العذراء البريطانية",
    "جزر ماريانا الشماليه": "جزر ماريانا الشمالية",
    "جزيرة بوفية": "جزيرة بوفيه",
    "جزيره الكريسماس": "جزيرة الكريسماس",
    "جزيره بوفيه": "جزيرة بوفيه",
    "جزيره مان": "جزيرة مان",
    "جزيره نورفولك": "جزيرة نورفولك",
    "جمةورية أفريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "جمةورية افريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "جمةورية التشيك": "جمهورية التشيك",
    "جمةورية الدومينيكان": "جمهورية الدومينيكان",
    "جمهورية افريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "جمهوريه أفريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "جمهوريه افريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "جمهوريه التشيك": "جمهورية التشيك",
    "جمهوريه الدومينيكان": "جمهورية الدومينيكان",
    "جنوب افريقيا": "جنوب أفريقيا",
    "جورجيا الجنوبيه": "جورجيا الجنوبية",
    "دانمارك": "الدانمارك",
    "رأس الأخضر": "الرأس الأخضر",
    "راس الاخضر": "الرأس الأخضر",
    "ساموا الأمريكيه": "ساموا الأمريكية",
    "ساموا الامريكية": "ساموا الأمريكية",
    "ساموا الامريكيه": "ساموا الأمريكية",
    "سانت ةيلينا": "سانت هيلينا",
    "سعودية": "السعودية",
    "سعوديه": "السعودية",
    "سلفادور": "السلفادور",
    "سنغافوره": "سنغافورة",
    "سنغال": "السنغال",
    "سودان": "السودان",
    "سودان الجنوبي": "السودان الجنوبي",
    "سويد": "السويد",
    "صحراء الغربية": "الصحراء الغربية",
    "صحراء الغربيه": "الصحراء الغربية",
    "صومال": "الصومال",
    "صين": "الصين",
    "عراق": "العراق",
    "غابون": "الغابون",
    "غويانا الفرنسيه": "غويانا الفرنسية",
    "غينيا الاستوائيه": "غينيا الاستوائية",
    "فلبين": "الفلبين",
    "كاليدونيا الجديده": "كاليدونيا الجديدة",
    "كاميرون": "الكاميرون",
    "كوريا الجنوبيه": "كوريا الجنوبية",
    "كوريا الشماليه": "كوريا الشمالية",
    "كونغو": "الكونغو",
    "كويت": "الكويت",
    "مالديف": "المالديف",
    "مانيا": "المانيا",
    "مدينه الفاتيكان": "مدينة الفاتيكان",
    "مغرب": "المغرب",
    "مكسيك": "المكسيك",
    "مملكة المتحدة": "المملكة المتحدة",
    "مملكه المتحده": "المملكة المتحدة",
    "نرويج": "النرويج",
    "نمسا": "النمسا",
    "نيجر": "النيجر",
    "نيذرلاندز": "النيذرلاندز",
    "هند": "الهند",
    "ولايات المتحدة": "الولايات المتحدة",
    "ولايات المتحده": "الولايات المتحدة",
    "يابان": "اليابان",
    "يمن": "اليمن",
    "يونان": "اليونان",
}