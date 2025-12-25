import requests
from bs4 import BeautifulSoup
import re
import csv

# ==========================
# Ayarlar
# ==========================
fon_kod = "AGA"  # Fon kodu
fon_adi = "BEREKET EMEKLİLİK VE HAYAT A.Ş. ALTIN KATILIM EMEKLİLİK YATIRIM FONU"
period = "12"  # 12 aylık örnek

url = f"https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod={fon_kod}"


urlapi = "https://www.tefas.gov.tr/api/DB/BindCompareFundReturnGraph?startDate=2024-01-01&endDate=2025-10-29&fonKod=AGA"
res = requests.get(urlapi)
print(res.json())

# ==========================
# 1. Session aç ve GET isteği ile hidden inputları al
# ==========================
session = requests.Session()
res = session.get(url)
soup = BeautifulSoup(res.text, "html.parser")

viewstate = soup.find("input", {"id": "__VIEWSTATE"})["value"]
eventvalidation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]
viewstategenerator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]

# ==========================
# 2. POST payload'u oluştur
# ==========================
payload = {
    "ctl00$MainContent$ScriptManager1": f"ctl00$MainContent$UpdatePanel1|ctl00$MainContent$RadioButtonListPeriod$5",
    "ctl00$MainContent$TextBoxFund": f"{fon_kod} - {fon_adi}",
    "ctl00$MainContent$RadioButtonListPeriod": period,
    "__EVENTTARGET": "ctl00$MainContent$RadioButtonListPeriod$5",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEGENERATOR": viewstategenerator,
    "__EVENTVALIDATION": eventvalidation,
    "__ASYNCPOST": "true"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=AGA",
    "Origin": "https://www.tefas.gov.tr",
    "X-MicrosoftAjax": "Delta=true",
    "X-Requested-With": "XMLHttpRequest",
}

response = session.post(url, data=payload, headers=headers)
html = response.text

# ==========================
# 3. Highcharts verisini parse et
# ==========================
# Örnek: path koordinatları ve tarihleri çek
soup = BeautifulSoup(html, "html.parser")

# Tarihler (x-axis)
dates = [t.text for t in soup.find_all("tspan") if re.match(r"\d{2}\.\d{2}\.\d{4}", t.text)]

# Fiyatlar için path (stroke="#4572A7" olan çizgi)
path = soup.find("path", {"stroke": "#4572A7"})
coords = re.findall(r"[ML] ([\d\.]+) ([\d\.]+)", path["d"])
points = [(float(x), float(y)) for x, y in coords]

# Y ekseni dönüşümü (0.72-0.78 aralığı örnek)
y_min, y_max = 329.5, 10.5
v_min, v_max = 0.72, 0.78

def y_to_value(y):
    return v_min + (y_min - y) * (v_max - v_min) / (y_min - y_max)

# Tarih ve fiyat eşleştirme
data = []
for date, (x, y) in zip(dates[-len(points):], points):
    value = y_to_value(y)
    data.append((date, round(value, 6)))

# ==========================
# 4. CSV'ye kaydet
# ==========================
csv_file = f"{fon_kod}_data.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Tarih", "Fiyat"])
    writer.writerows(data)

print(f"{len(data)} veri kaydı {csv_file} dosyasına kaydedildi.")
