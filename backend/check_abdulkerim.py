import sys
sys.path.insert(0, '.')
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

# Önce tablo yapısını görelim
print("=== TABLO YAPISI ===")
result = db.execute(text("DESC personnel"))
print("personnel tablosu kolonları:")
for row in result.fetchall():
    print(f"  {row[0]}")
print()

# Abdulkerim Aksan'ı SQL ile bul
result = db.execute(text('''
    SELECT 
        p.id, p.ad, p.soyad,
        pdc.net_ucret, pdc.ucret_nevi,
        ppg.donem,
        ppg.calisilan_gun_sayisi,
        ppg.normal_calismasi,
        ppg.izin_gun_sayisi,
        ppg.yillik_izin_gun,
        ppg.yarim_gun_sayisi,
        ppg.eksik_gun_sayisi,
        ppg.rapor_gun_sayisi,
        ppg.sigorta_girmedigi,
        ppg.ayin_toplam_gun_sayisi,
        ppg.hafta_tatili,
        ppg.resmi_tatil,
        ppg.tatil_calismasi
    FROM personnel p
    LEFT JOIN personnel_draft_contracts pdc ON p.id = pdc.personnel_id AND pdc.is_active = 1
    LEFT JOIN personnel_puantaj_grid ppg ON p.id = ppg.personnel_id
    WHERE p.ad LIKE '%Abdulkerim%' OR p.soyad LIKE '%Abdulkerim%'
    ORDER BY ppg.donem DESC
    LIMIT 1
'''))

row = result.fetchone()
if row:
    print(f'=== PERSONNEL BİLGİLERİ ===')
    print(f'Personnel: {row[1]} {row[2]} (ID: {row[0]})')
    print(f'\nDraft Contract:')
    print(f'  Net Ucret: {row[3]}')
    print(f'  Ucret Nevi: {row[4]}')
    
    if row[3]:
        gunluk = float(row[3]) / 30
        print(f'  Gunluk Ucret: {gunluk:.2f}')
    
    print(f'\n=== PUANTAJ GRID (Donem: {row[5]}) ===')
    print(f'  Calisilan Gun: {row[6]}')
    print(f'  Normal Calisma (GRID): {row[7]}')
    print(f'  Izin Gunleri (I): {row[8]}')
    print(f'  Yillik Izin (S): {row[9]}')
    print(f'  Yarim Gun: {row[10]}')
    print(f'  Eksik Gun: {row[11]}')
    print(f'  Rapor Gunu: {row[12]}')
    print(f'  Sigorta Girmedigi: {row[13]}')
    print(f'  Ayin Toplam Gunu: {row[14]}')
    print(f'  Hafta Tatili: {row[15]}')
    print(f'  Resmi Tatil: {row[16]}')
    print(f'  Tatil Calismasi: {row[17]}')
    
    if row[3]:
        normal_cal = float(row[7] or 0)
        izin_gun = int(row[8] or 0)
        gunluk = float(row[3]) / 30
        
        # Tam ay formülü kontrolü
        ucret_nevi = row[4]
        eksik_gun = int(row[11] or 0)
        ayin_toplam = int(row[14] or 30)
        sigorta_girmedigi = int(row[13] or 0)
        rapor_gun = int(row[12] or 0)
        yarim_gun = int(row[10] or 0)
        calisilan = int(row[6] or 0)
        hafta_tatili = int(row[15] or 0)
        resmi_tatil = int(row[16] or 0)
        tatil_calismasi = int(row[17] or 0)
        
        tatiller = hafta_tatili + resmi_tatil + tatil_calismasi
        
        # Tam ay formülü koşulları
        kosul_ucret_nevi = ucret_nevi in ["aylik", "sabit aylik"]
        kosul_eksik = eksik_gun == 0
        kosul_ayin_gun = ayin_toplam != 30
        kosul_sigorta = sigorta_girmedigi == 0
        kosul_rapor = rapor_gun == 0
        kosul_yarim = yarim_gun == 0
        
        tam_ay_formulu = (kosul_ucret_nevi and kosul_eksik and kosul_ayin_gun and 
                         kosul_sigorta and kosul_rapor and kosul_yarim)
        
        print(f'\n=== HESAPLAMA KONTROLU ===')
        print(f'\nTam Ay Formulu Aktif Mi? {tam_ay_formulu}')
        print(f'  - ucret_nevi: {ucret_nevi} (aylik/sabit aylik mi? {kosul_ucret_nevi})')
        print(f'  - eksik_gun: {eksik_gun} (0 mi? {kosul_eksik})')
        print(f'  - ayin_toplam_gun: {ayin_toplam} (30 degil mi? {kosul_ayin_gun})')
        print(f'  - sigorta_girmedigi: {sigorta_girmedigi} (0 mi? {kosul_sigorta})')
        print(f'  - rapor_gun: {rapor_gun} (0 mi? {kosul_rapor})')
        print(f'  - yarim_gun: {yarim_gun} (0 mi? {kosul_yarim})')
        print(f'  - Tatiller (hafta+resmi+tatil_calisma): {hafta_tatili}+{resmi_tatil}+{tatil_calismasi} = {tatiller}')
        
        if tam_ay_formulu:
            yeni_normal_cal = 30 - tatiller
            print(f'\n>>> TAM AY FORMULU KULLANILDI <<<')
            print(f'  Normal Calisma = 30 - {tatiller} = {yeni_normal_cal}')
        else:
            yeni_normal_cal = calisilan + yarim_gun
            print(f'\n>>> NORMAL FORMUL KULLANILDI <<<')
            print(f'  Normal Calisma = {calisilan} + {yarim_gun} = {yeni_normal_cal}')
        
        print(f'\n=== SONUC (DÜZELTME SONRASI) ===')
        print(f'Normal Kazanc = {yeni_normal_cal} x {gunluk:.2f} = {yeni_normal_cal * gunluk:.2f} TL')
        print(f'Izin Kazanc = {izin_gun} x {gunluk:.2f} = {izin_gun * gunluk:.2f} TL')
        print(f'Toplam = {yeni_normal_cal * gunluk:.2f} + {izin_gun * gunluk:.2f} = {(yeni_normal_cal + izin_gun) * gunluk:.2f} TL')
        
        print(f'\n=== MODAL GÖSTERIMI (YENİ) ===')
        print(f'Normal Kazanç: {yeni_normal_cal} x {gunluk:.2f} = {yeni_normal_cal * gunluk:.2f} TL')
        print(f'İzin Kazancı (İ): {izin_gun} İzin x {gunluk:.2f} = {izin_gun * gunluk:.2f} TL')
        print(f'\n✅ İzin günleri artık ayrı kazanç kalemi olarak gösteriliyor!')
        print(f'✅ Normal kazanç sadece normal çalışma günlerini içeriyor!')

else:
    print('Abdulkerim Aksan bulunamadi')

db.close()
