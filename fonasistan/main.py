from fonasistan.models.fon_entity import FonEntity
from fonasistan.services.egm_api import EGMApiService
from fonasistan.services.fon_parser_service import FonParserService
from fonasistan.repository.fon_repository import FonRepository
from fonasistan.services.tefas_service import TefasService
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
import pandas as pd


API_KEY = "b5db1af9-f0c2-426a-86b2-9b78d0d733cd"

egm_service = EGMApiService(API_KEY)
parser = FonParserService()
tefas_service = TefasService()
repo = FonRepository()

def run_update():
    print("🚀 Fon güncelleme başlıyor...")

    # Fon listesini al
    fon_data = egm_service.fetch_fon_list()
    if not fon_data:
        print("⚠️ Fon verisi alınamadı.")
        return

    df = pd.DataFrame(fon_data)
    if 'value' not in df.columns:
        print("⚠️ Fon verisinde 'value' sütunu bulunamadı.")
        return

    for value in df['value']:
        # DB'de yoksa ekle
        fon_id = repo.get_fon_id_from_cache(value)

        if not fon_id:
            fon_detail = egm_service.fetch_fon_detail(value)
            if not fon_detail or "XmlData" not in fon_detail or not fon_detail["XmlData"]:
                continue

            fund_entity: FonEntity = parser.parse_fon_detail(fon_detail)
            fon_response = repo.insert_fon(fund_entity)
            fon_id = fon_response.data[0]["id"]
            print(f"💾 Yeni fon eklendi: {fund_entity.name} ({fund_entity.code})")

def run_fiyat_update():
    print("🚀 Fon fiyat güncelleme başlıyor...")
    start_date = repo.get_last_date()
    start_date += timedelta(days=1)
    end_date = datetime.now()
    records=[]
    batch_size=1000
    total_records=0
    if not start_date:
        start_date = end_date - relativedelta(months=3)
    tarih_fiyat_listesi = tefas_service.fetch_history(start_date, end_date)

    print(f"💾 {len(tarih_fiyat_listesi)}  Adet Fiyat Bulundu...")

    for row in tarih_fiyat_listesi:
        fon_id=repo.get_fon_id_from_cache(row["FONKODU"])
        tarih = datetime.strptime(row['TARIH'], "%Y-%m-%d").date()

        record = {
            "fon_id": fon_id,
            "fon_code": row["FONKODU"],
            "tarih": tarih.isoformat(),
            "fiyat": row["FIYAT"],
            "kisi_sayisi": row.get("KISISAYISI", 0),
            "portfoy_buyukluk": row.get("PORTFOYBUYUKLUK", 0),
            "tedpay_sayisi": row.get("TEDPAYSAYISI", 0)
        }
        records.append(record)
        if len(records) >= batch_size:
            total_records += len(records)
            repo.insert_fiyat_batch(records)
            records.clear()
    if records:
        total_records += len(records)
        repo.insert_fiyat_batch(records)

    print(f"💾 {total_records}  Fiyat Kayıt Edildi...")

if __name__ == "__main__":
    run_update()
    run_fiyat_update()


