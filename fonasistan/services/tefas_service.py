# fonasistan/services/tefas_service.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from playwright.sync_api import sync_playwright
from typing import List, Dict, Optional
import time
import pandas as pd

class TefasService:
    def __init__(self):
        self.url = "https://www.tefas.gov.tr/api/DB/BindHistoryInfo"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Origin": "https://www.tefas.gov.tr",
            "Referer": "https://www.tefas.gov.tr/TarihselVeriler.aspx",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-MicrosoftAjax": "Delta=true",
            "X-Requested-With": "XMLHttpRequest",
        }

    def _to_ddmmyyyy(self, d: datetime) -> str:
        return d.strftime("%d.%m.%Y")

    def fetch_history(self, start_date, end_date, fund_type="EMK"):
        """
        TEFAS günlük fon fiyatlarını çeker, WAF engelini aşmak için gerçek tarayıcı kullanır.
        :param fon_kod: Fon kodu
        :param start_date: datetime objesi
        :param end_date: datetime objesi
        :param fund_type: "EMK", "YAT", "BYF"
        :return: List[dict] (TARIH, FONKODU, FONUNVAN, FIYAT, TEDPAYSAYISI, KISISAYISI, PORTFOYBUYUKLUK, BORSABULTENFIYAT)
        """
        result = []

        with sync_playwright() as p:
            # Gerçek tarayıcı aç, headless=False
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # TEFAS sayfasını aç
            page.goto("https://www.tefas.gov.tr/TarihselVeriler.aspx")
            time.sleep(5)  # F5 cookie ve JS’in çalışması için bekle

            # Cookie'leri al
            cookies = {c['name']: c['value'] for c in context.cookies()}

            # POST isteğini tarayıcı üzerinden yap
            response = page.request.post(
                self.url,
                data={
                    "fontip": fund_type,
                    "bastarih": start_date.strftime("%d.%m.%Y"),
                    "bittarih": end_date.strftime("%d.%m.%Y"),
                    "sfontur": "",
                    "fongrup": "",
                    "fonturkod": "",
                    "fonunvantip": ""
                },
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Origin": "https://www.tefas.gov.tr",
                    "Referer": "https://www.tefas.gov.tr/TarihselVeriler.aspx",
                    "X-Requested-With": "XMLHttpRequest",
                    "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
                }
            )

            text = response.text()
            if "<html>" in text:
                print("⚠ WAF tarafından engellendi. Cookie/JS çalışması tamam mı kontrol et.")
                browser.close()
                return []

            data = response.json()
            df = pd.DataFrame(data.get("data", []))
            if df.empty:
                browser.close()
                return []

            # Data'yı dict listesi olarak al
            for _, row in df.iterrows():
                tarih_iso = datetime.fromtimestamp(int(row["TARIH"]) / 1000).strftime("%Y-%m-%d")
                result.append({
                    "TARIH": tarih_iso,
                    "FONKODU": row.get("FONKODU"),
                    "FONUNVAN": row.get("FONUNVAN"),
                    "FIYAT": row.get("FIYAT"),
                    "TEDPAYSAYISI": row.get("TEDPAYSAYISI"),
                    "KISISAYISI": row.get("KISISAYISI"),
                    "PORTFOYBUYUKLUK": row.get("PORTFOYBUYUKLUK"),
                    "BORSABULTENFIYAT": row.get("BORSABULTENFIYAT")
                })

            browser.close()
        return result