"""View düzeltme scripti"""
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='muhasebe_sistem',
    charset='utf8mb4'
)

cursor = conn.cursor()

# View'i düzelt
sql = """
DROP VIEW IF EXISTS v_personnel_calendar;

CREATE OR REPLACE VIEW v_personnel_calendar AS
SELECT 
    pda.id,
    pda.personnel_id,
    p.sicil_no as personel_kodu,
    pda.tckn,
    pda.adi_soyadi,
    pda.attendance_date,
    pda.gun_adi,
    pda.donem,
    pda.gun_tipi,
    pda.calisma_durumu,
    pda.giris_saati,
    pda.cikis_saati,
    pda.normal_saat,
    pda.fazla_mesai_saat,
    pda.tatil_mesai_saat,
    (pda.normal_saat + pda.fazla_mesai_saat + pda.tatil_mesai_saat) as toplam_saat,
    CASE 
        WHEN pda.yillik_izin > 0 THEN 'Yillik Izin'
        WHEN pda.ucretsiz_izin > 0 THEN 'Ucretsiz Izin'
        WHEN pda.rapor > 0 THEN 'Rapor'
        WHEN pda.dogum_izin > 0 THEN 'Dogum Izni'
        WHEN pda.evlenme_izin > 0 THEN 'Evlenme Izni'
        WHEN pda.babalik_izin > 0 THEN 'Babalik Izni'
        ELSE NULL
    END as izin_turu,
    cc.name as santiye,
    cc.code as santiye_kodu,
    (pda.gunluk_kazanc + pda.fm_kazanc + pda.tatil_kazanc) as gunluk_toplam_kazanc,
    pda.aciklama
FROM personnel_daily_attendance pda
LEFT JOIN personnel p ON pda.personnel_id = p.id
LEFT JOIN cost_centers cc ON pda.cost_center_id = cc.id
"""

for statement in sql.split(';'):
    statement = statement.strip()
    if statement:
        cursor.execute(statement)

conn.commit()
print("✅ View düzeltildi!")

cursor.close()
conn.close()
