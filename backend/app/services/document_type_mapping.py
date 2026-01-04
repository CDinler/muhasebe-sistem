"""
Document Types Code Mapping
YEVMIYE_KAYDI_SABLONU.md'deki kodlar ile database'deki kodlar arasında eşleştirme
"""

# YEVMIYE_KAYDI_SABLONU.md kodları → Database kodları
YEVMIYE_TO_DB_MAPPING = {
    # FATURA kategorisi
    'ALIS_FATURASI': 'ALIS_FATURA',
    'SATIS_FATURASI': 'SATIS_FATURA',
    'IADE_FATURASI': 'IADE_FATURA',
    # HAKEDIS_FATURASI: Ayni
    # PROFORMA_FATURA: Ayni
    
    # BANKA kategorisi
    'VIRMAN': 'BANKA_VIRMAN',
    # BANKA_TAHSILAT: Ayni
    # BANKA_TEDIYE: Ayni
    # DEKONT: Ayni
    
    # MUHASEBE kategorisi
    'MAHSUP_FISI': 'MAHSUP',
    'YEVMIYE_FISI': 'YEVMIYE',
    'ACILIS_FISI': 'ACILIS',
    'DUZELTICI_FIS': 'DUZELTME',
    # KAPANIS_FISI: Ayni
    # TERS_KAYIT: Ayni
}

# Database kodları → YEVMIYE_KAYDI_SABLONU.md kodları (reverse mapping)
DB_TO_YEVMIYE_MAPPING = {v: k for k, v in YEVMIYE_TO_DB_MAPPING.items()}


def get_db_code(yevmiye_code: str) -> str:
    """YEVMIYE_KAYDI_SABLONU.md kodunu database koduna çevir"""
    return YEVMIYE_TO_DB_MAPPING.get(yevmiye_code, yevmiye_code)


def get_yevmiye_code(db_code: str) -> str:
    """Database kodunu YEVMIYE_KAYDI_SABLONU.md koduna çevir"""
    return DB_TO_YEVMIYE_MAPPING.get(db_code, db_code)


# Document type kategorileri
DOCUMENT_CATEGORIES = {
    'FATURA': 'Fatura',
    'KASA': 'Kasa',
    'BANKA': 'Banka',
    'CEK_SENET': 'Çek/Senet',
    'PERSONEL': 'Personel',
    'GIDER': 'Gider',
    'VERGI': 'Vergi',
    'MUHASEBE': 'Muhasebe',
    'STOK': 'Stok',
}

# Document subtype kategorileri
SUBTYPE_CATEGORIES = {
    'E_BELGE': 'E-Belge',
    'MANUEL': 'Manuel',
    'OTOMATIK': 'Otomatik',
}
