from dataclasses import dataclass, field
from typing import List
from datetime import date

@dataclass
class FonKarsilastirmaOlcut:
    olcut: str
    oran: float

@dataclass
class FonPortfoyDagilim:
    dagilim_adi: str
    piy_oran: float

@dataclass
class FonEntity:
    code: str
    name: str
    type: str
    firma: str
    faizli: str
    risk_degeri: str
    yatirim_stratejisi: str
    portfoy_dagilimlari: List[FonPortfoyDagilim] = field(default_factory=list)
    karsilastirma_olcutleri: List[FonKarsilastirmaOlcut] = field(default_factory=list)

@dataclass
class FonGunlukFiyat:
    fon_id:int             # Fon id
    fon_code: str          # Fon kodu, örn: "AGA"
    tarih: date            # Tarih, datetime.date objesi
    fiyat: float           # Günlük fiyat
    kisi_sayisi: float = 0 # Opsiyonel, kişi sayısı
    portfoy_buyukluk: float = 0 # Opsiyonel, portföy büyüklüğü
    tedpay_sayisi: float = 0    # Opsiyonel, tedpay sayısı