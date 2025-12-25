import requests
import pandas as pd
from datetime import datetime

def fetch_tefas_history_info(fon_kod, start_date, end_date, fund_type="YAT"):
    """
    TEFAS BindHistoryInfo uç noktasından veri çeker.
    :param fon_kod: Fon kodu (örneğin "AGA")
    :param start_date: Başlangıç tarih stringi "DD.MM.YYYY"
    :param end_date: Bitiş tarih stringi "DD.MM.YYYY"
    :param fund_type: Fon tipi kodu ("YAT", "EMK", "BYF") – R paketi referanslı.
    :return: Pandas DataFrame
    """
    url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/TarihselVeriler.aspx",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-MicrosoftAjax": "Delta=true",
        "X-Requested-With": "XMLHttpRequest",
    }
    payload = {
        "fontip": fund_type,
        "bastarih": start_date,
        "bittarih": end_date,
        "fonkod": fon_kod,
        "sfontur": "",
        "fongrup": "",
        "fonturkod": "",
        "fonunvantip": ""
    }

    resp = requests.post(url, headers=headers, data=payload)
    resp.raise_for_status()
    data = resp.json()

    # Varsayım: data["data"] alanında liste halinde kayıtlar var

    df = pd.DataFrame(data.get("data", []))
    pairs = list(zip(df["TARIH"], df["FIYAT"]))
    converted = [
        (datetime.fromtimestamp(int(ts) / 1000).strftime("%Y-%m-%d"), fiyat)
        for ts, fiyat in pairs
    ]
    return converted

# Örnek kullanım:
history = fetch_tefas_history_info("AGA", "01.10.2025", "28.10.2025", fund_type="EMK")
print(history)