from  fonasistan.config import supabase
from fonasistan.models.fon_entity import FonEntity, FonGunlukFiyat
from datetime import date, datetime


class FonRepository:
    def __init__(self):
        self.fiyat_table = "fon_gunluk_fiyatlar"
        self.table_name = "fons"
        self._fon_dict = None  # cache

    def load_fon_dict(self):
        """Fon tablosundaki tüm kayıtları key=fon_kodu, value=id olarak cache’e alır"""
        fons = supabase.table(self.table_name).select("id","code").execute()
        self._fon_dict = {f["code"]: f["id"] for f in fons.data}
        return self._fon_dict

    def get_fon_id_from_cache(self, code: str):
        """Önceden yüklenmiş dict’ten fon_id getirir"""
        if self._fon_dict is None:
            self.load_fon_dict()
        return self._fon_dict.get(code)

    def insert_fon(self, fon: FonEntity):
        try:
            data = {
                "code": fon.code,
                "name": fon.name,
                "type": fon.type,
                "firma": fon.firma,
                "faizli": fon.faizli,
                "risk_degeri": fon.risk_degeri,
                "yatirim_stratejisi": fon.yatirim_stratejisi
            }

            fon_response = supabase.table("fons").insert(data).execute()
            fon_id=fon_response.data[0]["id"]

            portfoy_list = [
                {"fon_id": fon_id, "dagilim_adi": p.dagilim_adi, "piy_oran": p.piy_oran}
                for p in fon.portfoy_dagilimlari
            ]
            supabase.table("fon_portfoy_dagilimlari").insert(portfoy_list).execute()

            olcut_list = [
                {"fon_id": fon_id, "olcut": k.olcut, "oran": k.oran}
                for k in fon.karsilastirma_olcutleri
            ]
            if len(olcut_list)>0:
                supabase.table("fon_karsilastirma_olcutleri").insert(olcut_list).execute()

            return fon_response
        except Exception as e:
            print(f"Hata oluştu: {e}")
            # Hata olursa rollback benzeri işlem — fon kaydını geri al
            if 'fon_id' in locals():
                self.supabase.table("fons").delete().eq("id", fon_id).execute()
                print(f"Hata nedeniyle fon kaydı silindi (id={fon_id})")
            raise e

    def exists(self, code: str) -> bool:
        """Fon kodu DB'de var mı kontrol eder"""
        result = supabase.table(self.table_name).select("id").eq("code", code).execute()
        return len(result.data) > 0

    def get_fon_id(self, code: str) -> int | None:
        """Fon koduna göre DB'deki id'yi döner, yoksa None"""
        result = supabase.table(self.table_name).select("id").eq("code", code).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        return None

    def insert_fiyat_batch(self, fiyat_listesi: list):
        """Birden fazla fiyat kaydını Supabase'e toplu ekler."""
        if not fiyat_listesi:
            return

        try:
            supabase.table(self.fiyat_table).insert(fiyat_listesi).execute()
            print(f"✅ {len(fiyat_listesi)} kayıt Supabase'e eklendi.")
        except Exception as e:
            print(f"❌ Toplu fiyat ekleme hatası: {e}")

    def insert_fiyat(self, fiyat: FonGunlukFiyat):
        try:
            # Eğer aynı fon ve tarih zaten varsa insert yapma
            if self.exists_fiyat_tarih(fiyat.fon_code, fiyat.tarih):
                print(f"Fiyat zaten mevcut: {fiyat.fon_code} - {fiyat.tarih}")
                return

            data = {
                "fon_id": getattr(fiyat, "fon_id", None),  # fon_id ekleniyor
                "fon_code": fiyat.fon_code,
                "tarih": fiyat.tarih.isoformat(),
                "fiyat": fiyat.fiyat,
                "kisi_sayisi": fiyat.kisi_sayisi,
                "portfoy_buyukluk": fiyat.portfoy_buyukluk,
                "tedpay_sayisi": fiyat.tedpay_sayisi
            }

            supabase.table(self.fiyat_table).insert(data).execute()
            print(f"✅ Günlük fiyat kaydedildi: {fiyat.fon_code} - {fiyat.tarih}")

        except Exception as e:
            print(f"Günlük fiyat eklenirken hata oluştu: {e}")
            raise e

    # --- Günlük fiyat exists kontrol ---
    def exists_fiyat_tarih(self, fon_code: str, tarih: date) -> bool:
        result = supabase.table(self.fiyat_table).select("id")\
            .eq("fon_code", fon_code)\
            .eq("tarih", tarih.isoformat())\
            .execute()
        return len(result.data) > 0

    def get_last_date(self) -> date | None:
        # 'tarih' alanına göre azalan sıralama yap ve ilk kaydı al
        result = supabase.table(self.fiyat_table) \
            .select("tarih") \
            .order("tarih", desc=True) \
            .limit(1) \
            .execute()

        if result.data:
            return datetime.fromisoformat(result.data[0]["tarih"]).date()
        return None

    def get_last_date_from_fon_code(self, fon_code: str) -> date|None:
        # 'tarih' alanına göre azalan sıralama yap ve ilk kaydı al
        result = supabase.table(self.fiyat_table) \
            .select("tarih") \
            .eq("fon_code", fon_code) \
            .order("tarih", desc=True) \
            .limit(1) \
            .execute()

        if result.data:
            return datetime.fromisoformat(result.data[0]["tarih"]).date()
        return None
    