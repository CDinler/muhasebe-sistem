"""
Merkezi fiş numarası yönetimi
Tüm fişler sıralı ve kesintisiz olmalı: F00000001, F00000002, ...
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Optional
import re


def get_next_transaction_number(db: Session, prefix: str = "F", commit: bool = True) -> str:
    """
    Sıradaki fiş numarasını döndür
    
    Args:
        db: Database session
        prefix: Fiş öneki (F, BORDRO, vb.)
        commit: True ise commit yapar (normal kullanım), False ise rollback edilebilir (preview)
    
    Returns:
        str: Sıradaki fiş numarası (örn: F00025001)
    
    Kurallar:
    - Format: F + 8 haneli sayı (F00000001, F00000002, ...)
    - Sıralı ve kesintisiz ilerler
    - Her dönem/tip için ayrı seri yok, tümü tek seride
    """
    
    # transaction_counter tablosundan atomik olarak yeni numara al
    # Tablo yoksa otomatik oluştur
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS transaction_counter (
            id INT PRIMARY KEY DEFAULT 1,
            last_number INT NOT NULL
        )
    """))
    db.flush()
    
    # İlk kayıt yoksa ekle
    check = db.execute(text("SELECT COUNT(*) FROM transaction_counter WHERE id = 1")).scalar()
    if check == 0:
        db.execute(text("INSERT INTO transaction_counter (id, last_number) VALUES (1, 0)"))
        db.flush()

    # Atomik olarak sayaç artır (iki ayrı query)
    db.execute(text("UPDATE transaction_counter SET last_number = last_number + 1 WHERE id = 1"))
    
    # Güncel değeri oku
    result = db.execute(text("SELECT last_number FROM transaction_counter WHERE id = 1")).fetchone()
    next_num = result[0] if result else 1
    
    if commit:
        db.commit()

    return f"{prefix}{next_num:08d}"


def get_next_bordro_number(db: Session, donem: str) -> str:
    """
    Bordro için sıradaki fiş numarasını döndür
    
    UYARI: Artık bordro fişleri de ana seri içinde!
    Bu fonksiyon sadece geriye dönük uyumluluk için.
    
    Args:
        db: Database session
        donem: Dönem (örn: 2025-11)
    
    Returns:
        str: Sıradaki fiş numarası (örn: F00025001)
    """
    # Artık bordro da ana seriden numara alır
    return get_next_transaction_number(db)


def validate_transaction_number(transaction_number: str) -> bool:
    """
    Fiş numarası formatını kontrol et
    
    Geçerli formatlar:
    - F00000001 (ana seri)
    - F00025000 (ana seri)
    
    Args:
        transaction_number: Kontrol edilecek fiş numarası
    
    Returns:
        bool: Geçerli ise True
    """
    # F + 8 haneli sayı
    pattern = r'^F\d{8}$'
    return bool(re.match(pattern, transaction_number))


def check_sequence_gaps(db: Session) -> list:
    """
    Fiş numaralarında boşluk var mı kontrol et
    
    Returns:
        list: Boşluk varsa [(from_num, to_num, gap), ...]
    """
    result = db.execute(text("""
        SELECT transaction_number
        FROM transactions
        WHERE transaction_number REGEXP '^F[0-9]{8}$'
        ORDER BY transaction_number
    """)).fetchall()
    
    gaps = []
    prev_num = None
    
    for row in result:
        num = int(row[0][1:])  # F00025000 -> 25000
        
        if prev_num and (num - prev_num) > 1:
            gaps.append({
                'from': f"F{prev_num:08d}",
                'to': f"F{num:08d}",
                'gap': num - prev_num - 1
            })
        
        prev_num = num
    
    return gaps


def delete_transaction_by_number(db: Session, transaction_number: str) -> bool:
    """
    Fiş numarasına göre fiş ve satırlarını sil
    
    Args:
        db: Database session
        transaction_number: Silinecek fiş numarası
    
    Returns:
        bool: Silme başarılı ise True
    """
    try:
        # Önce transaction_lines'ı sil
        db.execute(text("""
            DELETE FROM transaction_lines
            WHERE transaction_id IN (
                SELECT id FROM transactions WHERE transaction_number = :num
            )
        """), {"num": transaction_number})
        
        # Sonra transaction'ı sil
        result = db.execute(text("""
            DELETE FROM transactions WHERE transaction_number = :num
        """), {"num": transaction_number})
        
        db.commit()
        return result.rowcount > 0
    except Exception as e:
        db.rollback()
        raise e


def get_transaction_stats(db: Session) -> dict:
    """
    Fiş istatistiklerini getir
    
    Returns:
        dict: {
            'total': Toplam fiş sayısı,
            'last_number': Son fiş numarası,
            'next_number': Sıradaki fiş numarası,
            'gaps': Boşluk sayısı
        }
    """
    result = db.execute(text("""
        SELECT 
            COUNT(*) as total,
            MAX(transaction_number) as last_num
        FROM transactions
        WHERE transaction_number REGEXP '^F[0-9]{8}$'
    """)).fetchone()
    
    total = result[0] if result else 0
    last_num = result[1] if result and result[1] else None
    
    gaps = check_sequence_gaps(db)
    
    return {
        'total': total,
        'last_number': last_num,
        'next_number': get_next_transaction_number(db),
        'gaps_count': len(gaps),
        'gaps': gaps[:10]  # İlk 10 boşluk
    }
