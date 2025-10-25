import xml.etree.ElementTree as ET
from fonasistan.models.fon_entity import FonEntity, FonKarsilastirmaOlcut, FonPortfoyDagilim

class FonParserService:

    @staticmethod
    def parse_fon_detail(fon_detail) -> FonEntity | None:
        if not fon_detail or "XmlData" not in fon_detail or not fon_detail["XmlData"]:
            print("⚠️ XmlData yok veya boş!")
            return None

        xml_data = fon_detail["XmlData"]
        root = ET.fromstring(f"<root>{xml_data}</root>")

        entity = FonEntity(
            code=root.findtext('FUND_CODE', default=""),
            name=root.findtext('FUND_NAME', default=""),
            type=root.findtext('FUND_TYPE', default=""),
            firma=root.findtext('TITLE', default=""),
            faizli=root.findtext('FAIZLI', default=""),
            risk_degeri=root.findtext('FON_RISK_DEGER', default=""),
            yatirim_stratejisi=root.findtext('FON_YATIRIM_ARAC', default=""),
        )

        # Portföy dağılımı
        for item in root.findall('.//PORTFOY_DAGILIM_LIST/PORTFOY_DAGILIM'):
            dagilim = FonPortfoyDagilim(
                piy_deger=item.findtext('PIY_DEGER', "").strip(),
                piy_oran=float(item.find('PIY_ORAN').text.strip().replace(',', '.'))
            )
            entity.portfoy_dagilimlari.append(dagilim)

        # Karşılaştırma ölçütleri
        for olcut in root.findall('.//FON_KARSILASTIRMA_OLCUT'):
            entity.karsilastirma_olcutleri.append(FonKarsilastirmaOlcut(
                olcut=olcut.findtext('KARSILASTIRMA_OLCUT', ""),
                oran=float(olcut.findtext('KARSILASTIRMA_OLCUT_ORAN').strip().replace(',', '.'))
            ))

        return entity
