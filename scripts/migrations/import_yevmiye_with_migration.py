"""
YEVMİYE KAYITLARINI CSV'DEN SİSTEME AKTARMA - ESKİ HESAP KODLARI DÖNÜŞÜMÜ
=========================================================================

KULLANIM:
python import_yevmiye_with_migration.py dosyaniz.csv

ÖZELLİKLER:
✅ ESKİ personel hesap kodlarını (335.00001) YENİ formata (335.TC) otomatik çevirir
✅ Migration backup tablosunu kullanır
✅ Mevcut fişlere dokunmaz
✅ İSTİSNA: F00026060 numaralı fiş varsa güncellenir
✅ Türkçe karakter desteği (UTF-8)

CSV'DE ESKİ FORMAT KULLANILABL:
- 335.00001 → 335.12345678901 (otomatik dönüşüm)
- 335.00002 → 335.98765432109 (otomatik dönüşüm)
"""

import sys
import csv
from pathlib import Path
from decimal import Decimal
from collections import defaultdict
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

SPECIAL_UPDATE_FIS = "F00026060"

def load_migration_map(engine):
    """Eski → yeni hesap kodu haritasını yükle (migration_backup + personnel)"""
    print("\n" + "="*100)
    print("🔄 ESKİ → YENİ HESAP KODU DÖNÜŞÜM HARİTASI YÜKLENIYOR")
    print("="*100)
    
    with engine.connect() as conn:
        # Yöntem 1: Personnel tablosundan TC → yeni kod mapping
        result = conn.execute(text("""
            SELECT CONCAT('335.', LPAD(p.id, 5, '0')) as old_code,
                   CONCAT('335.', p.tckn) as new_code
            FROM personnel p
            WHERE p.tckn IS NOT NULL
        """))
        
        migration_map = {row[0]: row[1] for row in result}
        
        # Yöntem 2: Migration backup'tan eski kodları al, personnel'den yeni kodları bul
        result = conn.execute(text("""
            SELECT DISTINCT mb.old_account_code, CONCAT('335.', p.tckn) as new_code
            FROM migration_335_backup mb
            JOIN personnel p ON p.tckn = mb.personnel_tckn
            WHERE mb.old_account_code IS NOT NULL
            AND p.tckn IS NOT NULL
        """))
        
        for row in result:
            migration_map[row[0]] = row[1]
        
        # Aktif accounts tablosundan TC hesaplarını al
        result = conn.execute(text("""
            SELECT code, id, name
            FROM accounts
            WHERE code LIKE '335.%'
            AND is_active = 1
        """))
        
        current_accounts = {row[0]: (row[1], row[2]) for row in result}
        
    print(f"✅ Migration haritası: {len(migration_map)} eski → yeni dönüşüm")
    print(f"✅ Aktif 335 hesapları: {len(current_accounts)} adet")
    
    # İlk 10 örnek göster
    if migration_map:
        print(f"\n🔄 Örnek Dönüşümler:")
        for old_code, new_code in list(migration_map.items())[:10]:
            print(f"   {old_code} → {new_code}")
    
    return migration_map, current_accounts

def convert_account_code(code, migration_map):
    """Hesap kodunu eski formatsa yeniye çevir"""
    # Özel düzeltme: 740.00069 → 740.00200
    if code == '740.00069':
        return '740.00200'
    # Eğer migration map'te varsa dönüştür
    if code in migration_map:
        return migration_map[code]
    # Değilse olduğu gibi döndür
    return code

def validate_csv(filename, migration_map):
    """CSV dosyasını doğrula ve hesap kodlarını dönüştür"""
    print("\n" + "="*100)
    print("📋 CSV DOSYASI DOĞRULAMA VE DÖNÜŞTÜRME")
    print("="*100)
    
    # CSV alan boyut limitini artır
    csv.field_size_limit(10 * 1024 * 1024)  # 10 MB
    
    # Türkçe Excel noktalı virgül kullanır (virgül metinde olabilir)
    # Başlık satırını kontrol et
    with open(filename, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline()
        
        # Başlıkta "transaction_number" varsa delimiter'ı tespit et
        if 'transaction_number' in first_line:
            delimiter = ';' if ';' in first_line else ','
        else:
            # Yoksa noktalı virgül daha fazla ise onu kullan
            delimiter = ';' if first_line.count(';') > first_line.count(',') else ','
        
        print(f"✅ Tespit edilen CSV ayırıcı: '{delimiter}'")
        f.seek(0)
        
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    
    print(f"\n✅ Toplam satır: {len(rows)}")
    
    print(f"\n✅ Toplam satır: {len(rows)}")
    
    # Kolon isimlerini kontrol et (transaction_numbe veya transaction_number)
    cols = rows[0].keys() if rows else []
    
    # Esnek kolon eşleştirme
    col_map = {}
    for col in cols:
        if col.startswith('transaction_numb'):
            col_map['transaction_number'] = col
        elif col == 'transaction_date':
            col_map['transaction_date'] = col
        elif col == 'account_id':
            col_map['account_id'] = col
        elif col == 'debit':
            col_map['debit'] = col
        elif col == 'credit':
            col_map['credit'] = col
    
    # Gerekli kolonları kontrol et
    required_cols = ['transaction_number', 'transaction_date', 'account_id', 'debit', 'credit']
    missing_cols = [col for col in required_cols if col not in col_map]
    
    if missing_cols:
        print(f"\n❌ HATA: Eksik kolonlar: {', '.join(missing_cols)}")
        print(f"\nBulunan kolonlar: {', '.join(cols)}")
        return None
    
    print(f"✅ Tüm gerekli kolonlar mevcut")
    
    # Kolon isimlerini normalize et
    if col_map['transaction_number'] != 'transaction_number':
        print(f"🔄 Kolon düzeltme: '{col_map['transaction_number']}' → 'transaction_number'")
        for row in rows:
            row['transaction_number'] = row[col_map['transaction_number']]
    
    # Hesap kodlarını dönüştür
    converted_count = 0
    conversion_log = []
    
    for row in rows:
        old_code = row['account_id']
        new_code = convert_account_code(old_code, migration_map)
        
        if old_code != new_code:
            converted_count += 1
            if len(conversion_log) < 10:
                conversion_log.append(f"   {old_code} → {new_code}")
        
        row['account_id'] = new_code  # Değişikliği uygula
    
    if converted_count > 0:
        print(f"\n🔄 HESAP KODU DÖNÜŞÜMLERI:")
        print(f"   Toplam dönüşüm: {converted_count} satır")
        for log in conversion_log:
            print(log)
        if converted_count > 10:
            print(f"   ... ve {converted_count - 10} dönüşüm daha")
    else:
        print(f"\n✅ Tüm hesap kodları zaten yeni formatta")
    
    # Fişleri grupla
    fis_groups = defaultdict(list)
    for row in rows:
        fis_groups[row['transaction_number']].append(row)
    
    print(f"\n📊 Toplam fiş sayısı: {len(fis_groups)}")
    
    # Denge kontrolü DEVRE DIŞI - tüm fişler olduğu gibi aktarılacak
    print(f"⚠️  Denge kontrolü devre dışı (kullanıcı isteği)")
    print(f"✅ Tüm fişler aktarılacak")
    
    return rows, fis_groups

def check_existing_and_accounts(engine, fis_groups, rows):
    """Mevcut fişleri ve hesapları kontrol et"""
    print("\n" + "="*100)
    print("🔍 MEVCUT FİŞLER VE HESAP KONTROLÜ")
    print("="*100)
    
    with engine.connect() as conn:
        # Mevcut fişleri kontrol et
        fis_numbers = list(fis_groups.keys())
        placeholders = ','.join([f"'{fis}'" for fis in fis_numbers])
        
        result = conn.execute(text(f"""
            SELECT transaction_number 
            FROM transactions
            WHERE transaction_number IN ({placeholders})
        """))
        
        existing_fis = set(row[0] for row in result)
        
        will_update = SPECIAL_UPDATE_FIS in existing_fis
        existing_fis_filtered = existing_fis - {SPECIAL_UPDATE_FIS}
        
        print(f"\n📊 CSV'deki fiş sayısı: {len(fis_numbers)}")
        print(f"⚠️  Sistemde MEVCUT: {len(existing_fis)} fiş")
        
        if will_update:
            print(f"🔄 GÜNCELLENECEK: {SPECIAL_UPDATE_FIS}")
        
        if existing_fis_filtered:
            print(f"⏭️  ATLANACAK: {len(existing_fis_filtered)} fiş")
        
        new_fis = set(fis_numbers) - existing_fis_filtered - {SPECIAL_UPDATE_FIS}
        print(f"✅ YENİ EKLENECEK: {len(new_fis)} fiş")
        
        # Hesap kodlarını kontrol et (artık hepsi dönüştürülmüş olmalı)
        account_codes = set(row['account_id'] for row in rows)
        placeholders_acc = ','.join([f"'{code}'" for code in account_codes])
        
        result = conn.execute(text(f"""
            SELECT code, id, name, is_active
            FROM accounts
            WHERE code IN ({placeholders_acc})
        """))
        
        account_map = {row[0]: (row[1], row[2], row[3]) for row in result}
        
        print(f"\n📊 CSV'deki hesap kodu sayısı: {len(account_codes)}")
        print(f"✅ Sistemde bulunan: {len(account_map)}")
        
        # Bulunamayan hesaplar
        missing_accounts = account_codes - set(account_map.keys())
        if missing_accounts:
            print(f"\n❌ Sistemde BULUNAMAYAN hesap kodları ({len(missing_accounts)} adet):")
            for code in sorted(missing_accounts)[:10]:
                print(f"   {code}")
            return None, None
        
        # Pasif hesaplar uyarısı
        inactive = [code for code, (_, _, active) in account_map.items() if not active]
        if inactive:
            print(f"\n⚠️  PASİF hesaplar ({len(inactive)} adet):")
            for code in inactive[:5]:
                print(f"   {code} - {account_map[code][1]}")
    
    return existing_fis_filtered, account_map

def import_transactions(engine, fis_groups, existing_fis, account_map):
    """Fişleri sisteme aktar"""
    print("\n" + "="*100)
    print("💾 YEVMİYE KAYITLARI AKTARILIYOR")
    print("="*100)
    
    # Türkiye formatını temizle
    def clean_decimal(value):
        """Türkiye sayı formatını temizle (binlik: nokta, ondalık: virgül)"""
        if not value or value.strip() == '':
            return Decimal('0')
        cleaned = str(value).strip().replace('.', '').replace(',', '.').replace(' ', '')
        try:
            return Decimal(cleaned)
        except:
            return Decimal('0')
    
    new_count = 0
    updated_count = 0
    skipped_count = 0
    
    with engine.begin() as conn:
        for fis_no, lines in fis_groups.items():
            try:
                if fis_no in existing_fis:
                    skipped_count += 1
                    continue
                
                # Özel fiş güncelleme
                if fis_no == SPECIAL_UPDATE_FIS:
                    conn.execute(text("""
                        DELETE tl FROM transaction_lines tl
                        JOIN transactions t ON t.id = tl.transaction_id
                        WHERE t.transaction_number = :fis_no
                    """), {'fis_no': fis_no})
                    
                    conn.execute(text("""
                        DELETE FROM transactions WHERE transaction_number = :fis_no
                    """), {'fis_no': fis_no})
                    
                    print(f"🔄 {fis_no} güncelleniyor...")
                    updated_count += 1
                else:
                    new_count += 1
                
                # İlk satırdan fiş bilgilerini al
                first_line = lines[0]
                
                transaction_date = first_line['transaction_date']
                
                # Excel seri numarası kontrolü ve dönüşümü
                if transaction_date and transaction_date.isdigit():
                    # Excel seri numarası (örn: 45991)
                    from datetime import datetime, timedelta
                    excel_epoch = datetime(1899, 12, 30)  # Excel epoch
                    days = int(transaction_date)
                    actual_date = excel_epoch + timedelta(days=days)
                    transaction_date = actual_date.strftime('%Y-%m-%d')
                    print(f"📅 Tarih düzeltme - Excel seri {days} → {transaction_date}")
                
                accounting_period = first_line.get('accounting_period') or transaction_date[:7]
                
                # İsteğe bağlı alanlar
                cost_center_id = first_line.get('cost_center_id') or None
                description = first_line.get('description') or ''
                document_type = first_line.get('document_type') or None
                document_subtype = first_line.get('document_subtype') or None
                document_number = first_line.get('document_number') or None
                
                # Transaction ekle
                result = conn.execute(text("""
                    INSERT INTO transactions 
                    (transaction_number, transaction_date, accounting_period, 
                     cost_center_id, description, document_type, document_subtype, document_number)
                    VALUES 
                    (:fis_no, :date, :period, :cc_id, :desc, :doc_type, :doc_subtype, :doc_no)
                """), {
                    'fis_no': fis_no,
                    'date': transaction_date,
                    'period': accounting_period,
                    'cc_id': cost_center_id,
                    'desc': description,
                    'doc_type': document_type,
                    'doc_subtype': document_subtype,
                    'doc_no': document_number
                })
                
                transaction_id = result.lastrowid
                
                # Transaction lines ekle
                for line in lines:
                    account_code = line['account_id']  # Artık dönüştürülmüş
                    account_id = account_map[account_code][0]
                    
                    line_desc = line.get('line_description') or ''
                    debit = clean_decimal(line.get('debit', '0'))
                    credit = clean_decimal(line.get('credit', '0'))
                    quantity = clean_decimal(line.get('quantity', '0')) if line.get('quantity') else None
                    unit = line.get('unit') or None
                    
                    conn.execute(text("""
                        INSERT INTO transaction_lines
                        (transaction_id, account_id, description, debit, credit, quantity, unit)
                        VALUES
                        (:trans_id, :acc_id, :desc, :debit, :credit, :qty, :unit)
                    """), {
                        'trans_id': transaction_id,
                        'acc_id': account_id,
                        'desc': line_desc,
                        'debit': debit,
                        'credit': credit,
                        'qty': quantity,
                        'unit': unit
                    })
                
            except Exception as e:
                print(f"\n❌ HATA - {fis_no}: {e}")
                raise
    
    print(f"\n✅ TAMAMLANDI:")
    print(f"   Yeni eklenen: {new_count} fiş")
    print(f"   Güncellenen: {updated_count} fiş")
    print(f"   Atlanan: {skipped_count} fiş")
    
    return new_count, updated_count, skipped_count

def main():
    if len(sys.argv) < 2:
        print("KULLANIM: python import_yevmiye_with_migration.py dosyaniz.csv")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    if not Path(filename).exists():
        print(f"❌ Dosya bulunamadı: {filename}")
        sys.exit(1)
    
    # Database bağlantısı
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # 1. Migration haritasını yükle
        migration_map, current_accounts = load_migration_map(engine)
        
        # 2. CSV'yi doğrula ve dönüştür
        result = validate_csv(filename, migration_map)
        if not result:
            print("\n❌ CSV doğrulama başarısız!")
            sys.exit(1)
        
        rows, fis_groups = result
        
        # 3. Mevcut fişleri ve hesapları kontrol et
        existing_fis, account_map = check_existing_and_accounts(engine, fis_groups, rows)
        if account_map is None:
            print("\n❌ Hesap kontrolü başarısız!")
            sys.exit(1)
        
        # 4. Özet göster ve onay al
        print("\n" + "="*100)
        print("📊 ÖZET")
        print("="*100)
        
        new_count = len(fis_groups) - len(existing_fis)
        if SPECIAL_UPDATE_FIS in fis_groups:
            if SPECIAL_UPDATE_FIS in existing_fis:
                new_count -= 1  # Güncelleme sayılmaz
                print(f"🔄 Güncellenecek: 1 fiş ({SPECIAL_UPDATE_FIS})")
            else:
                print(f"✅ Yeni eklenecek (özel fiş dahil): {new_count} fiş")
        
        print(f"✅ Yeni eklenecek: {new_count} fiş")
        print(f"⏭️  Atlanacak (mevcut): {len(existing_fis)} fiş")
        
        response = input("\nDevam edilsin mi? (E/H): ").strip().upper()
        if response != 'E':
            print("❌ İşlem iptal edildi")
            sys.exit(0)
        
        # 5. İçeri aktar
        import_transactions(engine, fis_groups, existing_fis, account_map)
        
        print("\n" + "="*100)
        print("🎉 BAŞARIYLA TAMAMLANDI!")
        print("="*100)
        
    except Exception as e:
        print(f"\n❌ HATA: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
