import csv
from fonasistan.models.fon_entity import FonEntity, FonGunlukFiyat
from fonasistan.repository.fon_repository import FonRepository
from datetime import datetime, date
from typing import List
from pathlib import Path

repo=FonRepository()
repo.load_fon_dict()

def parse_turkish_number(value: str) -> float:
    """Türkçe sayı formatını (1.234.567,89) float'a çevirir"""
    if not value:
        return 0.0
    value = value.replace('.', '').replace(',', '.')
    try:
        return float(value)
    except ValueError:
        return 0.0

def import_fon_csv(file_path: str, fon_id_start: int = 1) -> int:

    with open(file_path, encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        row_count = 0
        records = []
        batch_size=1000
        for row in reader:
            tarih = datetime.strptime(row['Tarih'], "%d.%m.%Y").date()
            fon_code=row['Fon Kodu']

            fon_id=repo.get_fon_id_from_cache(fon_code)

            record = {
                "fon_id": fon_id,
                "fon_code": fon_code,
                "tarih": tarih.isoformat(),
                "fiyat": parse_turkish_number(row['Fiyat']),
                "kisi_sayisi": parse_turkish_number(row['Kişi Sayısı']),
                "portfoy_buyukluk": parse_turkish_number(row['Fon Toplam Değer']),
                "tedpay_sayisi": parse_turkish_number(row['Tedavüldeki Pay Sayısı'])
            }

            records.append(record)
            if len(records) >= batch_size:
                repo.insert_fiyat_batch(records)
                records.clear()
            row_count += 1
    if records:
        repo.insert_fiyat_batch(records)
    return row_count

if __name__ == "__main__":
    base_path = Path(r"C:\Sources\pyton\FonVeri")

    all_fonlar: List[FonGunlukFiyat] = []
    fon_id_counter = 1

    for csv_file in base_path.glob("*.csv"):
        print(f"📄 Dosya okunuyor: {csv_file.name}")
        count = import_fon_csv(csv_file, fon_id_start=fon_id_counter)
        fon_id_counter += count

    print(f"\nToplam {len(all_fonlar)} kayıt okundu.\n")

    for f in all_fonlar[:10]:  # ilk 10 kaydı gösterelim
        print(f)