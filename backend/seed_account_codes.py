"""Seed bordro account codes to system_config"""
from app.core.database import SessionLocal
from app.models.system_config import SystemConfig

db = SessionLocal()

account_codes = [
    ('bordro_maliyet_acc_id', '5535', 'Bordro maliyet hesabı (varsayılan)'),
    ('bordro_maliyet_cc31_acc_id', '5556', 'Bordro maliyet hesabı (cost_center_id=31 için)'),
    ('bordro_g_vergi_acc_id', '728', 'Gelir vergisi hesabı'),
    ('bordro_d_vergi_acc_id', '729', 'Damga vergisi hesabı'),
    ('bordro_sgk_isci_prim_acc_id', '731', 'SGK işçi primi hesabı'),
    ('bordro_sgk_isveren_prim_acc_id', '732', 'SGK işveren primi hesabı'),
    ('bordro_sgk_isci_isz_acc_id', '733', 'SGK işçi işsizlik hesabı'),
    ('bordro_sgk_isveren_isz_acc_id', '734', 'SGK işveren işsizlik hesabı'),
    ('bordro_bes_kesinti_acc_id', '735', 'BES kesinti hesabı'),
    ('bordro_icra_kesinti_acc_id', '736', 'İcra kesinti hesabı'),
    ('bordro_haz_kat_payi_acc_id', '744', 'Hazine katkı payı (SSK teşvik) hesabı'),
]

for key, value, description in account_codes:
    existing = db.query(SystemConfig).filter(SystemConfig.config_key == key).first()
    if existing:
        existing.config_value = value
        existing.description = description
        print(f"✅ Güncellendi: {key} = {value}")
    else:
        config = SystemConfig(
            config_key=key,
            config_value=value,
            config_type='NUMBER',
            category='BORDRO_HESAP_KODLARI',
            description=description
        )
        db.add(config)
        print(f"✅ Eklendi: {key} = {value}")

db.commit()
print(f"\n✅ Toplam {len(account_codes)} hesap kodu eklendi/güncellendi")
db.close()
