"""
E-FATURA İLİŞKİLERİNİ KORUYARAK YEVMİYE KAYITLARINI YENİDEN YÜKLEME
SEÇENEK A: Tamamen yeniden yükle + E-fatura ilişkilerini kur
"""

import pandas as pd
from app.core.database import SessionLocal
from sqlalchemy import text
from datetime import datetime
import sys
import logging
import os

# TÜM SQL LOGLARINI KAPAT
logging.basicConfig(level=logging.CRITICAL)
logging.getLogger('sqlalchemy').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.orm').setLevel(logging.CRITICAL)

# Environment variable olarak da kapat
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'
os.environ['SQLALCHEMY_WARN_20'] = '0'

# CSV dosyası
CSV_FILE = r"C:\Users\CAGATAY\OneDrive\Desktop\MUHASEBE_ANALIZ_v2\muhasebe kayıtları son guncel hali1.csv"

def print_step(step_num, message):
    print(f"\n{'='*80}")
    print(f"ADIM {step_num}: {message}")
    print('='*80)

def main():
    # SQL engine loglarını session başında da kapat
    db = SessionLocal()
    db.bind.echo = False
    
    try:
        print("="*80)
        print("E-FATURA İLİŞKİLERİNİ KORUYARAK YEVMİYE GÜNCELLEME")
        print("="*80)
        
        # ============================================================
        # ADIM 1: MEVCUT DURUM ANALİZİ
        # ============================================================
        print_step(1, "Mevcut Durum Analizi")
        
        # Transaction sayısı
        result = db.execute(text("SELECT COUNT(*) FROM transactions"))
        tx_count = result.scalar()
        print(f"Mevcut transaction sayısı: {tx_count:,}")
        
        # Transaction lines sayısı
        result = db.execute(text("SELECT COUNT(*) FROM transaction_lines"))
        line_count = result.scalar()
        print(f"Mevcut transaction_lines sayısı: {line_count:,}")
        
        # E-fatura bağlantılı transaction sayısı
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM einvoices 
            WHERE transaction_id IS NOT NULL
        """))
        einvoice_linked = result.scalar()
        print(f"E-faturaya bağlı transaction: {einvoice_linked:,}")
        
        if tx_count == 0:
            print("\n[!] Database boş! Doğrudan yükleme yapılacak.")
            has_data = False
        else:
            has_data = True
        
        # ============================================================
        # ADIM 2: E-FATURA İLİŞKİLERİNİ YEDEKLE
        # ============================================================
        print_step(2, "E-Fatura İlişkilerini Yedekleme")
        
        einvoice_backup = {}
        
        if has_data:
            result = db.execute(text("""
                SELECT 
                    e.id as einvoice_id,
                    e.invoice_number,
                    e.transaction_id,
                    t.transaction_number
                FROM einvoices e
                LEFT JOIN transactions t ON e.transaction_id = t.id
                WHERE e.transaction_id IS NOT NULL
            """))
            
            for row in result:
                einvoice_backup[row.invoice_number] = {
                    'einvoice_id': row.einvoice_id,
                    'old_transaction_id': row.transaction_id,
                    'transaction_number': row.transaction_number
                }
            
            print(f"✅ {len(einvoice_backup)} e-fatura ilişkisi yedeklendi")
            
            # İlk 5 örnek göster
            if einvoice_backup:
                print("\nÖrnek ilişkiler:")
                for i, (inv_num, data) in enumerate(list(einvoice_backup.items())[:5]):
                    print(f"  {inv_num} → {data['transaction_number']}")
        
        # ============================================================
        # ADIM 3: CSV'Yİ OKUMA VE DOĞRULAMA
        # ============================================================
        print_step(3, "CSV Okuma ve Doğrulama")
        
        df = pd.read_csv(CSV_FILE, sep=';', encoding='utf-8-sig', dtype={'account_code': str})
        print(f"CSV Satır Sayısı: {len(df):,}")
        print(f"Kolonlar: {list(df.columns)}")
        
        # Borç-Alacak dengesi kontrolü
        df['debit'] = pd.to_numeric(df['debit'], errors='coerce').fillna(0)
        df['credit'] = pd.to_numeric(df['credit'], errors='coerce').fillna(0)
        
        total_debit = df['debit'].sum()
        total_credit = df['credit'].sum()
        balance_diff = abs(total_debit - total_credit)
        
        print(f"\n💰 Borç Toplamı:   {total_debit:,.2f}")
        print(f"💰 Alacak Toplamı: {total_credit:,.2f}")
        print(f"💰 Fark:           {balance_diff:,.2f}")
        
        if balance_diff > 50:
            print(f"\n❌ HATA: Borç-Alacak dengesi tutmuyor! Fark: {balance_diff:.2f} TL")
            return
        
        print(f"✅ CSV dengesi OK")
        
        # ============================================================
        # ADIM 4: ONAY AL
        # ============================================================
        print_step(4, "Kullanıcı Onayı")
        
        if has_data:
            print(f"\n⚠️ DİKKAT! Şu işlemler yapılacak:")
            print(f"  1. {line_count:,} transaction_lines silinecek")
            print(f"  2. {tx_count:,} transaction silinecek")
            print(f"  3. CSV'den {len(df):,} satır yüklenecek")
            print(f"  4. {len(einvoice_backup)} e-fatura ilişkisi geri kurulacak")
        else:
            print(f"\n✅ YENİ YÜKLEME:")
            print(f"  CSV'den {len(df):,} satır yüklenecek")
        
        # Otomatik devam et
        print("\n✅ İşlem başlatılıyor...")
        
        # ============================================================
        # ADIM 5: ESKİ VERİLERİ SİLME
        # ============================================================
        print_step(5, "Eski Verileri Silme")
        
        if has_data:
            # E-fatura ilişkilerini geçici olarak NULL yap
            db.execute(text("UPDATE einvoices SET transaction_id = NULL"))
            print("✅ E-fatura ilişkileri geçici olarak NULL yapıldı")
            
            # Transaction lines sil
            db.execute(text("DELETE FROM transaction_lines"))
            print("✅ transaction_lines silindi")
            
            # Transactions sil
            db.execute(text("DELETE FROM transactions"))
            print("✅ transactions silindi")
            
            db.commit()
            print("✅ Silme işlemi tamamlandı")
        
        # ============================================================
        # ADIM 6: YENİ VERİLERİ YÜKLEME
        # ============================================================
        print_step(6, "Yeni Verileri Yükleme")
        
        # Transaction'ları grupla
        grouped = df.groupby('transaction_number')
        total_transactions = len(grouped)
        
        print(f"Toplam {total_transactions:,} fiş yüklenecek...")
        
        transaction_map = {}  # transaction_number -> new_id
        loaded_count = 0
        start_time = datetime.now()
        
        for tx_num, tx_df in grouped:
            # İlk satırdan header bilgileri al
            first_row = tx_df.iloc[0]
            
            # Transaction ekle
            tx_date = pd.to_datetime(first_row['transaction_date']).date()
            # accounting_period yoksa tarihten oluştur
            period = str(first_row['accounting_period']) if pd.notna(first_row['accounting_period']) else f"{tx_date.year}-{tx_date.month:02d}"
            
            db.execute(text("""
                INSERT INTO transactions (
                    transaction_number, transaction_date, accounting_period,
                    cost_center_id, description, document_type, 
                    document_subtype, document_number
                ) VALUES (
                    :tx_num, :tx_date, :period,
                    :cost_center, :desc, :doc_type,
                    :doc_subtype, :doc_num
                )
            """), {
                'tx_num': str(tx_num),
                'tx_date': tx_date,
                'period': period,
                'cost_center': int(first_row['cost_center_id']) if pd.notna(first_row['cost_center_id']) else None,
                'desc': str(first_row['description']) if pd.notna(first_row['description']) else None,
                'doc_type': str(first_row['document_type']) if pd.notna(first_row['document_type']) else None,
                'doc_subtype': str(first_row['document_subtype']) if pd.notna(first_row['document_subtype']) else None,
                'doc_num': str(first_row['document_number']) if pd.notna(first_row['document_number']) else None
            })
            
            # MariaDB için LAST_INSERT_ID() kullan
            result = db.execute(text("SELECT LAST_INSERT_ID()"))
            new_tx_id = result.scalar()
            transaction_map[str(tx_num)] = new_tx_id
            
            # Transaction lines ekle
            for _, line_row in tx_df.iterrows():
                # Account ID bul
                account_code = str(line_row['account_code']).strip()
                account_result = db.execute(text("""
                    SELECT id FROM accounts WHERE code = :code
                """), {'code': account_code})
                account_row = account_result.fetchone()
                
                if not account_row:
                    print(f"\n⚠️ UYARI: Hesap bulunamadı: {account_code} - Atlanıyor")
                    continue
                
                account_id = account_row[0]
                
                # Transaction line ekle
                db.execute(text("""
                    INSERT INTO transaction_lines (
                        transaction_id, account_id, description,
                        debit, credit, quantity, unit
                    ) VALUES (
                        :tx_id, :acc_id, :desc,
                        :debit, :credit, :qty, :unit
                    )
                """), {
                    'tx_id': new_tx_id,
                    'acc_id': account_id,
                    'desc': str(line_row['line_description']) if pd.notna(line_row['line_description']) else None,
                    'debit': float(line_row['debit']) if pd.notna(line_row['debit']) else 0,
                    'credit': float(line_row['credit']) if pd.notna(line_row['credit']) else 0,
                    'qty': float(line_row['quantity']) if pd.notna(line_row['quantity']) else None,
                    'unit': str(line_row['unit']) if pd.notna(line_row['unit']) else None
                })
            
            loaded_count += 1
            
            # Progress göster - HER 100 fişte
            if loaded_count % 100 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                percent = (loaded_count / total_transactions) * 100
                avg_time = elapsed / loaded_count
                remaining = (total_transactions - loaded_count) * avg_time
                
                print(f"\r⏳ {loaded_count:,} / {total_transactions:,} ({percent:.1f}%) - Kalan: {int(remaining/60)} dk {int(remaining%60)} sn", end='', flush=True)
            
            # Her 1000 fişte commit
            if loaded_count % 1000 == 0:
                db.commit()
                print()  # Yeni satır
        
        db.commit()
        print()  # Son satır
        print(f"✅ {loaded_count:,} fiş ve satırları yüklendi")
        print(f"⏱️ Toplam süre: {int((datetime.now() - start_time).total_seconds() / 60)} dakika")
        
        # ============================================================
        # ADIM 7: E-FATURA İLİŞKİLERİNİ GERİ KURMA
        # ============================================================
        print_step(7, "E-Fatura İlişkilerini Geri Kurma")
        
        if einvoice_backup:
            restored_count = 0
            not_found_count = 0
            
            for invoice_num, backup_data in einvoice_backup.items():
                tx_number = backup_data['transaction_number']
                
                if tx_number in transaction_map:
                    new_tx_id = transaction_map[tx_number]
                    
                    db.execute(text("""
                        UPDATE einvoices 
                        SET transaction_id = :new_id
                        WHERE id = :einvoice_id
                    """), {
                        'new_id': new_tx_id,
                        'einvoice_id': backup_data['einvoice_id']
                    })
                    
                    restored_count += 1
                else:
                    not_found_count += 1
                    print(f"\n⚠️ UYARI: Transaction bulunamadı: {tx_number} (e-fatura: {invoice_num})")
            
            db.commit()
            print(f"✅ {restored_count} e-fatura ilişkisi geri kuruldu")
            if not_found_count > 0:
                print(f"⚠️ {not_found_count} e-fatura ilişkisi kurulamadı")
        else:
            print("ℹ️ E-fatura ilişkisi yoktu")
        
        # ============================================================
        # ADIM 8: DOĞRULAMA
        # ============================================================
        print_step(8, "Doğrulama")
        
        # Transaction sayısı
        result = db.execute(text("SELECT COUNT(*) FROM transactions"))
        new_tx_count = result.scalar()
        print(f"✅ Yüklenen transaction: {new_tx_count:,}")
        
        # Transaction lines sayısı
        result = db.execute(text("SELECT COUNT(*) FROM transaction_lines"))
        new_line_count = result.scalar()
        print(f"✅ Yüklenen transaction_lines: {new_line_count:,}")
        
        # E-fatura ilişkisi
        result = db.execute(text("""
            SELECT COUNT(*) 
            FROM einvoices 
            WHERE transaction_id IS NOT NULL
        """))
        new_einvoice_linked = result.scalar()
        print(f"✅ E-faturaya bağlı transaction: {new_einvoice_linked:,}")
        
        # 335 hesapları kontrolü
        result = db.execute(text("""
            SELECT COUNT(DISTINCT a.code)
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE a.code LIKE '335.%'
        """))
        account_335_count = result.scalar()
        print(f"✅ 335 hesap sayısı: {account_335_count:,}")
        
        # 335 hesap TCKN uzunluk kontrolü
        result = db.execute(text("""
            SELECT 
                LENGTH(REPLACE(a.code, '335.', '')) as tckn_length,
                COUNT(*) as count
            FROM transaction_lines tl
            JOIN accounts a ON tl.account_id = a.id
            WHERE a.code LIKE '335.%'
            GROUP BY LENGTH(REPLACE(a.code, '335.', ''))
            ORDER BY tckn_length
        """))
        
        print("\n335 Hesap TCKN Uzunluk Dağılımı:")
        all_11_digit = True
        for row in result:
            print(f"  {row[0]} haneli: {row[1]:,} satır")
            if row[0] != 11:
                all_11_digit = False
        
        if all_11_digit:
            print("✅ Tüm 335 hesapları 11 haneli!")
        else:
            print("⚠️ Bazı 335 hesapları 11 haneli değil!")
        
        # Borç-Alacak dengesi kontrolü
        result = db.execute(text("""
            SELECT 
                SUM(debit) as total_debit,
                SUM(credit) as total_credit
            FROM transaction_lines
        """))
        row = result.fetchone()
        db_debit = float(row[0] or 0)
        db_credit = float(row[1] or 0)
        db_diff = abs(db_debit - db_credit)
        
        print(f"\n💰 Database Borç:   {db_debit:,.2f}")
        print(f"💰 Database Alacak: {db_credit:,.2f}")
        print(f"💰 Fark:            {db_diff:,.2f}")
        
        if db_diff < 50:
            print("✅ Borç-Alacak dengesi OK!")
        else:
            print(f"⚠️ Borç-Alacak dengesi tutmuyor: {db_diff:.2f} TL")
        
        # ============================================================
        # SONUÇ
        # ============================================================
        print("\n" + "="*80)
        print("GÜNCELLEME TAMAMLANDI!")
        print("="*80)
        print(f"✅ {new_tx_count:,} fiş yüklendi")
        print(f"✅ {new_line_count:,} satır yüklendi")
        print(f"✅ {new_einvoice_linked:,} e-fatura ilişkisi kuruldu")
        print(f"✅ {account_335_count:,} farklı 335 hesap")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ HATA: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        sys.exit(1)
    
    finally:
        db.close()

if __name__ == '__main__':
    main()
