import re
from typing import Any

LANGUAGES: dict[str, dict[str, str]] = {
    "tr": {
        "period_not_found": "Dönem bulunamadı: {} - Hisse: {}. Atlanıyor.",
        "no_valid_period": "Hiçbir geçerli dönem bulunamadı. Hisse: {}",
        "stock_done": "İşlem tamamlandı: {}",
        "saved_excel": "Excel dosyasına kaydedildi: {}",
        "all_done": "Tüm işlemler başarıyla tamamlandı.",
        "fetch_success": "{} tablosu başarıyla çekildi. Satır sayısı: {}",
        "invalid_period_format": "Geçersiz dönem formatı: {}",
        "invalid_quarter": "Geçersiz çeyrek: {} (dönem: {})",
        "stock_not_found": "Hisse kodu bulunamadı veya sayfa yüklenemedi: {}. Atlanıyor.",
    },
    "en": {
        "period_not_found": "Period not found: {} - Stock: {}. Skipping.",
        "no_valid_period": "No valid period found. Stock: {}",
        "stock_done": "Completed: {}",
        "saved_excel": "Saved to Excel: {}",
        "all_done": "All operations completed successfully.",
        "fetch_success": "{} table successfully fetched. Rows: {}",
        "invalid_period_format": "Invalid period format: {}",
        "invalid_quarter": "Invalid quarter: {} (period: {})",
        "stock_not_found": "Stock code not found or page could not be loaded: {}. Skipping.",
    }
}

TABS = [
    {"tab_href": "#finanslar", "tab_id": "finanslar", "name": "Financials"},
    {"tab_href": "#karlilik", "tab_id": "karlilik", "name": "Profitability"},
    {"tab_href": "#carpanlar", "tab_id": "carpanlar", "name": "Multiples"}
]

def get_localized_message(key: str, lang: str, *args: Any) -> str:
    template = LANGUAGES.get(lang, LANGUAGES["en"]).get(key, key)
    return template.format(*args) if args else template

period_regex = re.compile(r"^\d{4}/(03|06|09|12)$")

def previous_period(period: str, lang: str = "tr") -> str:
    try:
        year, quarter = period.split('/')
        year, quarter = int(year), int(quarter)
    except Exception:
        raise ValueError(get_localized_message("invalid_period_format", lang, period))
    if quarter == 3:
        return f"{year}/03"
    elif quarter == 6:
        return f"{year}/03"
    elif quarter == 9:
        return f"{year}/06"
    elif quarter == 12:
        return f"{year}/09"
    else:
        raise ValueError(get_localized_message("invalid_period_format", lang, period))

def format_period(period: str, lang: str = "tr") -> str:
    period = period.replace("-", "/").replace(" ", "/")
    match = re.match(r"^\s*(\d{4})\D?(03|06|09|12)\s*$", period)
    if not match:
        match_simple = re.match(r"^\s*(\d{4})\D?([369]|12)\s*$", period)
        if match_simple:
            year, q = match_simple.groups()
            if q in {"3", "6", "9"}:
                return f"{year}/0{q}"
            elif q == "12":
                return f"{year}/12"
        raise ValueError(get_localized_message("invalid_period_format", lang, period))
    year, q = match.groups()
    return f"{year}/{q}"