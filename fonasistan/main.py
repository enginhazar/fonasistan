from  fonasistan.services.egm_api import EGMApiService
from fonasistan.services.fon_parser_service import FonParserService
from fonasistan.models.fon_entity import FonEntity
import pandas as pd




def main():
    print("🚀 EGM Fon Bilgi Sistemi Başlatılıyor...")

    API_KEY= "b5db1af9-f0c2-426a-86b2-9b78d0d733cd"

    egm_service =EGMApiService(API_KEY)



    fon_data = egm_service.fetch_fon_list()
    if not fon_data:
        print("⚠️ Fon verisi alınamadı.")
        return

    # 3️⃣ DataFrame ile id/value sütununu al
    df = pd.DataFrame(fon_data)
    if 'value' not in df.columns:
        print("⚠️ Fon verisinde 'value' sütunu bulunamadı.")
        return

    parser = FonParserService()

    # 4️⃣ Her fonu çek ve entity’ye çevir
    for value in df['value']:
        print(f"Fetching fon detayları: {value}")
        fon_detail = egm_service.fetch_fon_detail(value)

        if not fon_detail or "XmlData" not in fon_detail or not fon_detail["XmlData"]:
            print(f"⚠️ Fon detayları boş: {value}")
            continue

        fund_entity: FonEntity = parser.parse_fon_detail(fon_detail)

        # 5️⃣ DB kaydı veya başka işleme
        print(f"💾 Fon entity hazır: {fund_entity.name} ({fund_entity.code})")
        # db_service.save_fund(fund_entity)  <-- ORM veya SQL ile kaydedebilirsin

    print("✅ İşlem tamamlandı.")


if __name__ == "__main__":
    main()