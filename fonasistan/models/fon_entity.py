from dataclasses import dataclass, field
from typing import List

@dataclass
class FonKarsilastirmaOlcut:
    olcut: str
    oran: float

@dataclass
class FonPortfoyDagilim:
    piy_deger: str
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