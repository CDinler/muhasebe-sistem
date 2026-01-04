"""
Kategori-Hesap Mapping sistemi
YEVMIYE_KAYDI_SABLONU.md'deki kararları uygular
"""
from decimal import Decimal

# Kategori → Hesap Mapping (ŞABLONDAN)
CATEGORY_ACCOUNT_MAP = {
    # Kategori 1: Hizmet Üretim Maliyeti
    'hizmet_uretim': '740',  # Alt hesap otomatik oluşturulacak: 740.XXXXX
    'elektrik': '740.00001',
    'su': '740.00002',
    'dogalgaz': '740.00003',
    'haberlesme': '740.00004',  # Telefon, internet (genel)
    'yakıt': '740.00005',
    'bakim_onarim': '740.00006',
    'nakliye': '740.00007',
    'sigorta': '740.00008',
    'danismanlik': '740.00009',
    
    # Kategori 2: Genel Yönetim Gideri
    'genel_yonetim': '770',
    'ofis_malzeme': '770.00001',
    'kira': '770.00002',
    'temizlik': '770.00003',
    'guvenlik': '770.00004',
    'noter_harç': '770.00005',
    'reklam': '770.00006',
    'seyahat': '770.00007',
    'abonman': '770.00201',  # Abonman Giderleri (Turkcell, internet aboneliği vs.)
    
    # Kategori 3: Ticari Mallar
    'ticari_mal': '153',
    'yedek_parca': '153.00001',
    'insaat_malzeme': '153.00002',
    
    # Kategori 4: Diğer Stoklar
    'diger_stok': '157',
    'alet_takım': '157.00001',
    'kimyasal': '157.00002',
    
    # Kategori 5: Demirbaş
    'demirbas_konteyner': '255.01',
    'demirbas_makine': '255.02',
    'demirbas_kalip': '255.03',
    'demirbas_ekipman': '255.04',
    'demirbas_is_makinasi': '255.05',
    
    # Kategori 6: Taşıt
    'tasit': '255.06',
}


def get_account_for_category(category: str, item_name: str = None, cost_center_name: str = None) -> str:
    """
    Kategori ve ürün adına göre hesap kodu döndürür
    
    Args:
        category: Kategori kodu
        item_name: Ürün/hizmet adı (opsiyonel)
        cost_center_name: Maliyet merkezi adı (opsiyonel)
    
    Returns:
        str: Hesap kodu
    """
    # Doğrudan mapping varsa kullan
    if category in CATEGORY_ACCOUNT_MAP:
        return CATEGORY_ACCOUNT_MAP[category]
    
    # Ürün adına göre otomatik kategori tespiti
    if item_name:
        item_lower = item_name.lower()
        
        # Elektrik
        if any(word in item_lower for word in ['elektrik', 'electric', 'enerji']):
            return CATEGORY_ACCOUNT_MAP['elektrik']
        
        # Su
        if any(word in item_lower for word in ['su', 'water', 'atıksu']):
            return CATEGORY_ACCOUNT_MAP['su']
        
        # Doğalgaz
        if any(word in item_lower for word in ['doğalgaz', 'gaz', 'natural gas']):
            return CATEGORY_ACCOUNT_MAP['dogalgaz']
        
        # Abonman Giderleri (Turkcell, Türk Telekom, internet paketleri)
        if any(word in item_lower for word in ['turkcell', 'vodafone', 'türk telekom', 'abonman', 'paket', 'tarife']):
            return CATEGORY_ACCOUNT_MAP['abonman']
        
        # Haberleşme (genel telefon, internet)
        if any(word in item_lower for word in ['telefon', 'internet', 'gsm']):
            return CATEGORY_ACCOUNT_MAP['haberlesme']
        
        # Yakıt
        if any(word in item_lower for word in ['yakıt', 'mazot', 'benzin', 'motorin', 'fuel', 'diesel']):
            return CATEGORY_ACCOUNT_MAP['yakıt']
        
        # Bakım Onarım
        if any(word in item_lower for word in ['bakım', 'onarım', 'tamir', 'repair', 'maintenance']):
            return CATEGORY_ACCOUNT_MAP['bakim_onarim']
        
        # Nakliye
        if any(word in item_lower for word in ['nakliye', 'taşıma', 'transport', 'kargo', 'lojistik']):
            return CATEGORY_ACCOUNT_MAP['nakliye']
        
        # Danışmanlık
        if any(word in item_lower for word in ['danışman', 'mühendis', 'proje', 'etüd', 'consulting']):
            return CATEGORY_ACCOUNT_MAP['danismanlik']
        
        # Kira
        if any(word in item_lower for word in ['kira', 'rent', 'lease']):
            return CATEGORY_ACCOUNT_MAP['kira']
        
        # Temizlik
        if any(word in item_lower for word in ['temizlik', 'cleaning']):
            return CATEGORY_ACCOUNT_MAP['temizlik']
    
    # Varsayılan: Cost center'a göre
    # Merkez dışında → 740 (Hizmet Üretim Maliyeti)
    # Merkez/Belirtilmemiş → 770 (Genel Yönetim Gideri)
    if cost_center_name and cost_center_name.upper() not in ['MERKEZ', 'GENEL', 'MERKEZ GENEL']:
        return '740'  # Hizmet Üretim Maliyeti (şantiye gideri)
    else:
        return '770'  # Genel Yönetim Gideri (merkez gideri)


def categorize_invoice_line(item_name: str, item_code: str = None) -> str:
    """
    Fatura satırını kategorize eder
    
    Args:
        item_name: Ürün/hizmet adı
        item_code: Ürün kodu (opsiyonel)
    
    Returns:
        str: Kategori kodu
    """
    item_lower = (item_name or '').lower()
    
    # Elektrik
    if any(word in item_lower for word in ['elektrik', 'electric']):
        return 'elektrik'
    
    # Haberleşme
    if any(word in item_lower for word in ['telefon', 'internet', 'gsm', 'turkcell']):
        return 'haberlesme'
    
    # Abonman (Turkcell, paket, tarife)
    if any(word in item_lower for word in ['abonman', 'paket', 'tarife']):
        return 'abonman'
    
    # Varsayılan
    return 'diger'


# Test
if __name__ == '__main__':
    test_items = [
        ("Elektrik Tüketimi", None),
        ("İnternet Abonelik Ücreti", None),
        ("Turkcell Faturası", None),
        ("Bakım Onarım Hizmeti", None),
        ("Genel Alış", None),
    ]
    
    print("KATEGORİ-HESAP MAPPING TESTİ")
    print("=" * 60)
    
    for item_name, item_code in test_items:
        category = categorize_invoice_line(item_name, item_code)
        account = get_account_for_category(category, item_name)
        print(f"{item_name:40} → {category:20} → {account}")
